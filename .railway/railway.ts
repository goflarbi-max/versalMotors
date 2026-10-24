import { defineRailway, github, preserve, project, service } from "railway/iac";

export default defineRailway((ctx) => {
  const api = service("versalmotors-api", {
    source: github("goflarbi-max/versalMotors", { branch: "main" }),
    healthcheck: "/health/ready",
    healthcheckTimeout: 300,
    replicas: { "europe-west4": 1 },
    env: {
      GEMINI_API_KEY: preserve(),
      GEMINI_MODEL: "gemini-3.8-flash",
      GEMINI_FALLBACK_MODELS: "gemini-3.5-flash-lite",
      GEMINI_MAX_ATTEMPTS: "2",
      VERSALMOTORS_ALLOWED_ORIGINS: ctx.shared.VERSALMOTORS_ALLOWED_ORIGINS,
      VERSALMOTORS_AUTH_USERS_JSON: preserve(),
      VERSALMOTORS_SECURE_COOKIES: "true",
      VERSALMOTORS_SESSION_HOURS: "8",
      VERSALMOTORS_SESSION_SECRET: preserve(),
    },
  });

  return project("VersalMotors", { resources: [api] });
});
