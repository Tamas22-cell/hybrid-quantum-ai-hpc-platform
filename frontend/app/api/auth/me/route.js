import { forwardJson } from "../../../../hpc-backend.js";

export async function GET(request) {
  return forwardJson("/auth/me", request);
}
