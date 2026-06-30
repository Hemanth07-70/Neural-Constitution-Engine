import { useState } from 'react'
import { PageWrapper } from '@/components/layout/PageWrapper'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Search, Filter, ShieldCheck, ShieldAlert, MoreHorizontal } from "lucide-react"

import { useAppStore } from '@/store/useAppStore'
import { apiClient } from '@/api/client'
import { useEffect } from 'react'

export function AuditCenter() {
  const [searchTerm, setSearchTerm] = useState("")
  const audits = useAppStore(state => state.audits)
  const setAudits = useAppStore(state => state.setAudits)
  const activeOrganization = useAppStore(state => state.activeOrganization)

  useEffect(() => {
    if (activeOrganization) {
      apiClient.get('/audits').then(res => {
        setAudits(res.data)
      }).catch(console.error)
    }
  }, [activeOrganization, setAudits])

  const filtered = audits.filter(a =>
    a.request.action.type.includes(searchTerm.toLowerCase()) ||
    a.request.actor.id.includes(searchTerm.toLowerCase()) ||
    a.id.includes(searchTerm.toLowerCase())
  )

  return (
    <PageWrapper>
      <div className="flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Audit Center</h2>
            <p className="text-muted-foreground mt-2">
              Immutable ledger of all agent decisions and enforcements.
            </p>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 w-full max-w-sm">
            <div className="relative w-full">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                type="search"
                placeholder="Search audits..."
                className="w-full bg-background pl-8"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          <Button variant="outline" className="gap-2">
            <Filter className="h-4 w-4" />
            Filters
          </Button>
        </div>

        <div className="border border-border rounded-md bg-card overflow-hidden">
          <Table>
            <TableHeader className="bg-muted/50">
              <TableRow>
                <TableHead className="w-[100px]">Audit ID</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Action</TableHead>
                <TableHead>Actor</TableHead>
                <TableHead>Environment</TableHead>
                <TableHead>Determining Rule</TableHead>
                <TableHead className="text-right">Timestamp</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="h-24 text-center text-muted-foreground">
                    No results.
                  </TableCell>
                </TableRow>
              ) : (
                filtered.map((audit) => (
                  <TableRow key={audit.id} className="group">
                    <TableCell className="font-mono text-xs font-medium">{audit.id}</TableCell>
                    <TableCell>
                      {audit.result.action === "block" ? (
                        <Badge variant="destructive" className="gap-1 rounded-sm px-1.5 font-normal">
                          <ShieldAlert className="h-3 w-3" /> Blocked
                        </Badge>
                      ) : (
                        <Badge variant="secondary" className="gap-1 rounded-sm px-1.5 font-normal text-emerald-500 bg-emerald-500/10 hover:bg-emerald-500/20">
                          <ShieldCheck className="h-3 w-3" /> {audit.result.action}
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell className="font-medium">{audit.request.action.type}</TableCell>
                    <TableCell className="text-muted-foreground">{audit.request.actor.id}</TableCell>
                    <TableCell>
                      <Badge variant="outline" className="font-normal text-xs">{audit.request.context.environment.name}</Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground text-sm">{audit.result.determining_rule_id || "Implicit"}</TableCell>
                    <TableCell className="text-right text-muted-foreground text-sm">{new Date(audit.recorded_at).toLocaleTimeString()}</TableCell>
                    <TableCell>
                      <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>
    </PageWrapper>
  )
}
