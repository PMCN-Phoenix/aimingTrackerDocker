import { useState } from 'react'
import { Button, Modal, message, theme } from 'antd'
import { ReloadOutlined } from '@ant-design/icons'

export default function UpdateDataButton() {
  const { token } = theme.useToken()
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
          backgroundColor: token.colorFillAlter,
          color: token.colorText,
          padding: '16px',
          borderRadius: '6px',
          border: `1px solid ${token.colorBorderSecondary}`,
        }}>
          {output}
        </pre>
      </Modal>
    </>
  )
}
