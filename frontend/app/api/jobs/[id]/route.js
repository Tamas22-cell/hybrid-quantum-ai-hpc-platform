import { forwardJson } from "../../../../hpc-backend.js";

export async function GET(request, { params }) {
  const { id } = await params;
  return forwardJson(`/jobs/${encodeURIComponent(id)}`, request);
}
