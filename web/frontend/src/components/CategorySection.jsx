import SubcategoryRow from './SubcategoryRow'

export default function CategorySection({ category, subcategories, onScenarioClick }) {
  return (
    <div style={{ marginBottom: '32px' }}>
      <h2 style={{ 
        borderBottom: '2px solid #1677ff', 
        paddingBottom: '8px',
        marginBottom: '16px'
      }}>
        {category}
      </h2>
      <div>
        {Object.entries(subcategories).map(([sub, scenarios]) => (
          <SubcategoryRow
            key={sub}
            subcategory={sub}
            scenarios={scenarios}
            onScenarioClick={onScenarioClick}
          />
        ))}
      </div>
    </div>
  )
}
