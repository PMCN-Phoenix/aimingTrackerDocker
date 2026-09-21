import { List, Typography } from 'antd'

const { Text, Paragraph } = Typography

export default function ReflectionList({ reflections }) {
  if (!reflections || reflections.length === 0) {
    return <Text type="secondary">暂无感悟</Text>
  }

  return (
    <List
      size="small"
      dataSource={reflections}
      renderItem={(item) => (
        <List.Item>
          <div>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              {new Date(item.time * 1000).toLocaleDateString()}
            </Text>
            <Paragraph style={{ margin: '4px 0 0 0' }}>
              {item.note}
            </Paragraph>
          </div>
        </List.Item>
      )}
    />
  )
}
