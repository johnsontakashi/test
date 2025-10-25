import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { SignedInUserS } from "./screens/SignedInUserS";

createRoot(document.getElementById("app") as HTMLElement).render(
  <StrictMode>
    <SignedInUserS />
  </StrictMode>,
);
