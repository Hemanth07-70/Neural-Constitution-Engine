import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AuditRecord, PlanValidationResult } from '@/api/types';

interface Organization {
  id: string;
  name: string;
  slug: string;
}

interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  organizations: Organization[];
}

interface AppState {
  // Auth State
  accessToken: string | null;
  refreshToken: string | null;
  user: UserProfile | null;
  activeOrganization: Organization | null;

  setAuth: (access: string, refresh: string, user: UserProfile) => void;
  setActiveOrganization: (orgId: string) => void;
  logout: () => void;

  // We keep this for quick UI updates in the active session, but Dashboard/Audits will fetch from API
  audits: AuditRecord[];
  planResults: PlanValidationResult[];

  setAudits: (audits: AuditRecord[]) => void;
  addAudit: (audit: AuditRecord) => void;
  addPlanResult: (result: PlanValidationResult) => void;
  clearHistory: () => void;
  // UI State
  customPlanJson: string | null;
  setCustomPlanJson: (json: string) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      audits: [],
      planResults: [],
      customPlanJson: null,

      accessToken: null,
      refreshToken: null,
      user: null,
      activeOrganization: null,

      setAuth: (access, refresh, user) => set({
        accessToken: access,
        refreshToken: refresh,
        user,
        activeOrganization: user.organizations?.[0] || null
      }),
      setActiveOrganization: (orgId) => set((state) => ({
        activeOrganization: state.user?.organizations.find(o => o.id === orgId) || null
      })),
      logout: () => set({ accessToken: null, refreshToken: null, user: null, activeOrganization: null, audits: [] }),

      setAudits: (audits) => set({ audits }),
      addAudit: (audit) => set((state) => ({
        audits: [audit, ...state.audits].slice(0, 100)
      })),
      addPlanResult: (result) => set((state) => ({ planResults: [result, ...state.planResults] })),
      clearHistory: () => set({ audits: [], planResults: [] }),
      setCustomPlanJson: (json) => set({ customPlanJson: json }),
    }),
    {
      name: 'nce-app-storage',
    }
  )
);
