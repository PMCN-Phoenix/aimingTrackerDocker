import { useState } from 'react'
import { Button, Modal, message } from 'antd'
import { ReloadOutlined } from '@ant-design/icons'

export default function UpdateDataButton() {
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [output, setOutput] = useState('')

  const handleUpdate = async () => {
    setLoading(true)
    setModalVisible(true)
    setOutput('正在更新数据...')

    try {
      const res = await fetch('http://127.0.0.1:8000/api/data/update', {
        method: 'POST',
      })
      const json = await res.json()

      if (json.code === 0) {
        setOutput(json.data.output || '更新完成！')
        message.success('数据更新成功')
      } else {
        setOutput(`更新失败: ${json.message}`)
        message.error('数据更新失败')
      }
    } catch (error) {
      setOutput(`更新失败: ${error.message}`)
      message.error('数据更新失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Button
        type="primary"
        icon={<ReloadOutlined />}
        loading={loading}
        onClick={handleUpdate}
        style={{ marginRight: '16px' }}
      >
        更新数据
      </Button>

      <Modal
        title="数据更新进度"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
      >
        <pre style={{ 
          whiteSpace: 'pre-wrap', 
          maxHeight: '400px', 
          overflow: 'auto',
          backgroundColor: '#f5f5f5',
          padding: '16px',
          borderRadius: '4px'
        }}>
          {output}
        </pre>
      </Modal>
    </>
  )
}
