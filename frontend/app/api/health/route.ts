import packageJson from "@/package.json";

export function GET() {
  return Response.json({
    status: "ok",
    version: packageJson.version,
  });
}
