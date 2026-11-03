import { useEffect, useState } from "react";
import { z } from "zod";

let authorization: string | null = null;
export function setCredentials(username: string, password: string) {
  const bytes = new TextEncoder().encode(`${username}:${password}`);
  authorization = `Basic ${btoa(Array.from(bytes, (byte) => String.fromCharCode(byte)).join(""))}`;
}
export function clearCredentials() {
  authorization = null;
}

export class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public status = 0,
  ) {
    super(message);
  }
}

export async function request<T>(
  path: string,
  schema: z.ZodType<T>,
  options: {
    signal?: AbortSignal;
    body?: unknown;
    rawBody?: string;
    method?: string;
  } = {},
): Promise<T> {
  const controller = new AbortController();
  const onAbort = () => controller.abort();
  options.signal?.addEventListener("abort", onAbort, { once: true });
  const timeout = window.setTimeout(() => controller.abort("timeout"), 180_000);
  const headers: Record<string, string> = { Accept: "application/json" };
  if (authorization) headers.Authorization = authorization;
  if (options.body !== undefined || options.rawBody !== undefined)
    headers["Content-Type"] = "application/json";
  try {
    const response = await fetch(path, {
      method:
        options.method ??
        (options.body === undefined && options.rawBody === undefined
          ? "GET"
          : "POST"),
      headers,
      body:
        options.rawBody ??
        (options.body === undefined ? undefined : JSON.stringify(options.body)),
      signal: controller.signal,
      cache: "no-store",
      credentials: "omit",
      redirect: "error",
    });
    const contentType = response.headers.get("content-type") ?? "";
    let payload: unknown = null;
    if (contentType.includes("json")) {
      try {
        payload = await response.json();
      } catch {
        throw new ApiError(
          "INVALID_API_RESPONSE",
          "The native API returned malformed JSON. Check the IRIS web application and gateway response.",
          response.status,
        );
      }
    }
    if (!response.ok) {
      const parsed = z
        .object({
          error: z
            .union([
              z.string(),
              z
                .object({
                  code: z.string().optional(),
                  message: z.string().optional(),
                })
                .passthrough(),
            ])
            .optional(),
          message: z.string().optional(),
          code: z.string().optional(),
        })
        .passthrough()
        .safeParse(payload);
      const detail = parsed.success ? parsed.data : null;
      const error = detail?.error;
      const code =
        (typeof error === "object" && error?.code) ||
        detail?.code ||
        (response.status === 401
          ? "AUTHENTICATION_REQUIRED"
          : response.status === 403
            ? "PERMISSION_DENIED"
            : `HTTP_${response.status}`);
      const message =
        (typeof error === "object" && error?.message) ||
        (typeof error === "string" ? error : null) ||
        detail?.message ||
        (response.status === 401
          ? "Sign in with your IRIS credentials to read this workspace."
          : response.status === 403
            ? "Your IRIS account does not have permission for this action."
            : "The native IRIS API could not complete this request.");
      throw new ApiError(code, message, response.status);
    }
    if (!contentType.includes("json"))
      throw new ApiError(
        "INVALID_API_RESPONSE",
        "The API returned non-JSON content. Check the IRIS web application and gateway route.",
        response.status,
      );
    const result = schema.safeParse(payload);
    if (!result.success) {
      const fields = result.error.issues
        .slice(0, 4)
        .map(
          (issue) => `${issue.path.join(".") || "response"}: ${issue.message}`,
        )
        .join("; ");
      throw new ApiError(
        "API_SCHEMA_MISMATCH",
        `The API response did not match the expected contract. ${fields}`,
        response.status,
      );
    }
    return result.data;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (options.signal?.aborted) throw error;
    if (controller.signal.aborted)
      throw new ApiError(
        "REQUEST_TIMEOUT",
        "IRIS did not answer within 180 seconds. The request may still be processing; refresh before creating a new run.",
      );
    throw new ApiError(
      "IRIS_UNAVAILABLE",
      "The native IRIS API could not be reached. Start the build 154 stack, then refresh.",
    );
  } finally {
    window.clearTimeout(timeout);
    options.signal?.removeEventListener("abort", onAbort);
  }
}

export type Resource<T> = {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
  checkedAt: Date | null;
};
export function useApi<T>(
  path: string | null,
  schema: z.ZodType<T>,
  refresh: number,
): Resource<T> {
  const [resource, setResource] = useState<Resource<T>>({
    data: null,
    loading: path !== null,
    error: null,
    checkedAt: null,
  });
  useEffect(() => {
    if (!path) {
      setResource({ data: null, loading: false, error: null, checkedAt: null });
      return;
    }
    const controller = new AbortController();
    setResource({ data: null, loading: true, error: null, checkedAt: null });
    request(path, schema, { signal: controller.signal })
      .then((data) => {
        if (!controller.signal.aborted)
          setResource({
            data,
            loading: false,
            error: null,
            checkedAt: new Date(),
          });
      })
      .catch((error: unknown) => {
        if (!controller.signal.aborted)
          setResource({
            data: null,
            loading: false,
            error:
              error instanceof ApiError
                ? error
                : new ApiError("REQUEST_FAILED", "Request failed."),
            checkedAt: new Date(),
          });
      });
    return () => controller.abort();
  }, [path, schema, refresh]);
  return resource;
}
