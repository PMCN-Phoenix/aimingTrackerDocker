import { useState } from 'react'
import { Input, Button, message } from 'antd'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createReflection } from '../api/client'

export default function ReflectionForm({ scenario, daylist }) {
  const [note, setNote] = useState('')
  const queryClient = useQueryClient()

  // 新增感悟的 mutation
  const createMutation = useMutation({
    mutationFn: (data) => createReflection(data),
    onSuccess: () => {
      message.success('感悟保存成功')
      setNote('')
      // 刷新感悟列表
      queryClient.invalidateQueries(['scenarioPopup', scenario])
      queryClient.invalidateQueries(['scenarioReflections', scenario])
    },
    onError: (error) => {
      message.error(`保存失败: ${error.message}`)
    },
  })

  const handleSubmit = () => {
    if (!note.trim()) {
      message.warning('请输入感悟内容')
      return
    }
    createMutation.mutate({
      scenario,
      note: note.trim(),
      daylist,
    })
  }

  return (
    <div style={{ marginTop: '16px' }}>
      <Input.TextArea
        rows={3}
        placeholder="写下今天的感悟..."
        value={note}
        onChange={(e) => setNote(e.target.value)}
      />
      <Button
        type="primary"
        style={{ marginTop: '8px' }}
        loading={createMutation.isPending}
        onClick={handleSubmit}
      >
        保存感悟
      </Button>
    </div>
  )
}
