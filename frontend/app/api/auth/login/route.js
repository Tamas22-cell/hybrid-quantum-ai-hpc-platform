import { establishSession } from "../../../../hpc-backend.js";

export async function POST(request) {
  return establishSession("/auth/login", request);
}
