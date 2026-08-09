/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_TACATDP_ACCESS_WRITE_ACTIONS_ENABLED?: string;
  readonly VITE_TACATDP_ACCESS_ASSIGN_FORM_WRITE_ENABLED?: string;
  readonly VITE_TACATDP_ACCESS_ONBOARDING_AUTOMATION_ENABLED?: string;
  readonly VITE_TACATDP_ACCESS_AUDIT_ONE_ROW_RESULT_ENABLED?: string;
  readonly VITE_TACATDP_ODK_RUNTIME_ENABLED?: string;
}

interface Window {
  __TACATDP_ODK_PLUGIN_LOAD_ERROR__?: string;
}
