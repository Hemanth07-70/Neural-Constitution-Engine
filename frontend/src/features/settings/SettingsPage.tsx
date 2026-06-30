import { useState, useEffect } from 'react'
import { PageWrapper } from '@/components/layout/PageWrapper'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useAppStore } from '@/store/useAppStore'
import { apiClient } from '@/api/client'
import { useToast } from '@/hooks/use-toast'
import { Key, Trash2, Copy, Check } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

interface ApiKey {
  id: string;
  name: string;
  prefix: string;
  created_at: string;
  revoked: boolean;
}

export function SettingsPage() {
  const [keys, setKeys] = useState<ApiKey[]>([])
  const [newKeyName, setNewKeyName] = useState('')
  const [createdKey, setCreatedKey] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const { activeOrganization } = useAppStore()
  const { toast } = useToast()

  const orgName = activeOrganization?.name || 'Demo Corporation'

  const fetchKeys = async () => {
    try {
      const url = activeOrganization ? `/api-keys?organization_id=${activeOrganization.id}` : '/api-keys'
      const res = await apiClient.get(url)
      setKeys(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    fetchKeys()
  }, [activeOrganization])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const payload: any = { name: newKeyName }
      if (activeOrganization?.id) {
        payload.organization_id = activeOrganization.id
      }
      const res = await apiClient.post('/api-keys/', payload)
      setCreatedKey(res.data.key)
      setNewKeyName('')
      fetchKeys()
      toast({ title: 'API Key Created', description: `Key generated for ${orgName}` })
    } catch (err: any) {
      toast({ title: 'Error', description: err.response?.data?.detail || err.message, variant: 'destructive' })
    }
  }

  const handleRevoke = async (id: string) => {
    try {
      const url = activeOrganization ? `/api-keys/${id}?organization_id=${activeOrganization.id}` : `/api-keys/${id}`
      await apiClient.delete(url)
      fetchKeys()
      toast({ title: 'API Key Revoked' })
    } catch (err: any) {
      toast({ title: 'Error', description: err.response?.data?.detail || err.message, variant: 'destructive' })
    }
  }

  const copyToClipboard = () => {
    if (createdKey) {
      navigator.clipboard.writeText(createdKey)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <PageWrapper>
      <div className="flex flex-col gap-8 max-w-5xl mx-auto">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">API Keys</h2>
          <p className="text-muted-foreground mt-2">Manage API keys for {orgName}.</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Create New Key</CardTitle>
            <CardDescription>Generate a new API key for programmatic access to the governance kernel.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreate} className="flex gap-4 items-end">
              <div className="flex-1 space-y-2">
                <Label htmlFor="name">Key Name</Label>
                <Input
                  id="name"
                  value={newKeyName}
                  onChange={e => setNewKeyName(e.target.value)}
                  placeholder="e.g. CI/CD Pipeline"
                  required
                />
              </div>
              <Button type="submit">Generate Key</Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Active Keys</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Prefix</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {keys.map((k) => (
                  <TableRow key={k.id}>
                    <TableCell className="font-medium">{k.name}</TableCell>
                    <TableCell className="font-mono text-xs">{k.prefix}...</TableCell>
                    <TableCell className="text-muted-foreground">{new Date(k.created_at).toLocaleDateString()}</TableCell>
                    <TableCell>
                      {k.revoked ? (
                        <Badge variant="destructive">Revoked</Badge>
                      ) : (
                        <Badge variant="secondary" className="bg-emerald-500/10 text-emerald-500">Active</Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" onClick={() => handleRevoke(k.id)} disabled={k.revoked}>
                        <Trash2 className="w-4 h-4 text-destructive" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
                {keys.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center text-muted-foreground py-8">
                      <Key className="w-8 h-8 mx-auto mb-2 opacity-20" />
                      No API keys generated yet.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>

      <Dialog open={!!createdKey} onOpenChange={(open) => !open && setCreatedKey(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>API Key Generated</DialogTitle>
            <DialogDescription>
              Please copy your API key now. You will not be able to see it again!
            </DialogDescription>
          </DialogHeader>
          <div className="flex items-center gap-2 mt-4 p-3 bg-muted rounded-md border border-border">
            <code className="flex-1 font-mono text-sm break-all">{createdKey}</code>
            <Button variant="outline" size="icon" onClick={copyToClipboard}>
              {copied ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </PageWrapper>
  )
}
