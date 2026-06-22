import React, { useState, useEffect } from 'react';

export const Resources = () => {
  const [resources, setResources] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [filters, setFilters] = useState<any>({
    stage: '',
    type: '',
    operator: ''
  });

  useEffect(() => {
    // Simulate fetching resources from backend
    setLoading(true);

    // Simulate API call with delay
    const timer = setTimeout(() => {
      // Mock data for resources
      const mockResources = [
        {
          id: 'res-001',
          name: 'Customer Discovery Workshop',
          operator: 'APII',
          type: 'training',
          description: 'Workshop on customer discovery techniques for early-stage startups.',
          eligibility_stages: ['validation', 'structuration'],
          domains_addressed: ['market', 'commercial_offer'],
          blockers_resolved: ['Limited market validation', 'Undefined business model'],
          geographic_scope: 'national',
          source_url: 'https://example.com/workshop',
          relevance_score: 0.92
        },
        {
          id: 'res-002',
          name: 'Business Model Canvas Training',
          operator: 'Tunisie Innovation',
          type: 'training',
          description: 'Learn to build and test business models using the Business Model Canvas framework.',
          eligibility_stages: ['validation', 'structuration', 'fundraising'],
          domains_addressed: ['commercial_offer', 'market'],
          blockers_resolved: ['Undefined business model', 'Missing revenue streams'],
          geographic_scope: 'national',
          source_url: 'https://example.com/bmc',
          relevance_score: 0.88
        },
        {
          id: 'res-003',
          name: 'Startup Act - Labellisation',
          operator: 'APII',
          type: 'support_program',
          description: 'Official label for innovative startups providing access to public financing and tax benefits.',
          eligibility_stages: ['structuration', 'fundraising', 'launch_planning'],
          domains_addressed: ['legal', 'financial', 'market'],
          blockers_resolved: ['No structured legal framework', 'No access to public financing'],
          geographic_scope: 'national',
          source_url: 'https://startup.gov.tn',
          relevance_score: 0.95
        },
        {
          id: 'res-004',
          name: 'BFPME Pre-Financing Guide',
          operator: 'BFPME',
          type: 'business_guide',
          description: 'Comprehensive guide to creating financial projections for startup financing applications.',
          eligibility_stages: ['validation', 'structuration', 'fundraising'],
          domains_addressed: ['financial'],
          blockers_resolved: ['Missing financial documentation', 'Undefined financial model'],
          geographic_scope: 'national',
          source_url: 'https://bfpme.com.tn/guide',
          relevance_score: 0.9
        },
        {
          id: 'res-005',
          name: 'ANPE Business Registration Portal',
          operator: 'ANPE',
          type: 'administrative_procedure',
          description: 'Online portal for registering business entities and obtaining legal recognition.',
          eligibility_stages: ['validation', 'structuration', 'fundraising'],
          domains_addressed: ['legal'],
          blockers_resolved: ['No legal entity', 'Informal business structure'],
          geographic_scope: 'national',
          source_url: 'https://anpe.nat.tn',
          relevance_score: 0.87
        },
        {
          id: 'res-006',
          name: 'Seed Financing - Innovation Startup Fund',
          operator: 'BFPME',
          type: 'financing_device',
          description: 'Seed financing for innovative startups with high growth potential.',
          eligibility_stages: ['structuration', 'fundraising'],
          domains_addressed: ['financial'],
          blockers_resolved: ['Insufficient capital', 'Limited access to financing'],
          amount_range: '50,000 - 200,000 TND',
          geographic_scope: 'national',
          source_url: 'https://bfpme.com.tn/funding/startup',
          relevance_score: 0.93
        }
      ];

      setResources(mockResources);
      setLoading(false);
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

  // Filter and search resources
  const filteredResources = resources.filter(resource => {
    // Text search
    if (searchQuery.trim() !== '') {
      const query = searchQuery.toLowerCase();
      const matchesName = resource.name.toLowerCase().includes(query);
      const matchesDescription = resource.description.toLowerCase().includes(query);
      if (!matchesName && !matchesDescription) {
        return false;
      }
    }

    // Stage filter
    if (filters.stage && !resource.eligibility_stages.includes(filters.stage)) {
      return false;
    }

    // Type filter
    if (filters.type && resource.type !== filters.type) {
      return false;
    }

    // Operator filter
    if (filters.operator && resource.operator.toLowerCase() !== filters.operator.toLowerCase()) {
      return false;
    }

    return true;
  });

  if (loading) {
    return (
      <div className="app">
        <div className="main-content">
          <div className="container">
            <h1>Resource Search</h1>
            <p className="text-muted">Search and explore Tunisian entrepreneurship support programs</p>
            <div className="card">
              <p>Loading resources...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app">
        <div className="main-content">
          <div className="container">
            <h1>Resource Search</h1>
            <p className="text-muted">Search and explore Tunisian entrepreneurship support programs</p>
            <div className="card">
              <h2>Error Loading Resources</h2>
              <p>{error}</p>
              <button className="btn btn-primary" onClick={() => window.location.reload()}>
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <div className="main-content">
        <div className="container">
          <h1>Resource Search</h1>
          <p className="text-muted">Search and explore Tunisian entrepreneurship support programs</p>

          <div className="card">
            <div className="card-header">
              <h2>Search & Filter Resources</h2>
            </div>
            <div className="card-content">
              <div className="grid grid-3">
                <div>
                  <input
                    type="text"
                    placeholder="Search resources..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="form-control"
                  />
                </div>
                <div>
                  <select
                    value={filters.stage}
                    onChange={(e) => setFilters({ ...filters, stage: e.target.value })}
                    className="form-control"
                  >
                    <option value="">All Stages</option>
                    <option value="validation">Validation</option>
                    <option value="structuration">Structuration</option>
                    <option value="fundraising">Fundraising</option>
                    <option value="launch_planning">Launch Planning</option>
                    <option value="growth">Growth</option>
                  </select>
                </div>
                <div>
                  <select
                    value={filters.type}
                    onChange={(e) => setFilters({ ...filters, type: e.target.value })}
                    className="form-control"
                  >
                    <option value="">All Types</option>
                    <option value="support_program">Support Program</option>
                    <option value="financing_device">Financing Device</option>
                    <option value="training">Training</option>
                    <option value="business_guide">Business Guide</option>
                    <option value="administrative_procedure">Administrative Procedure</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-2" style={{ marginTop: '1rem' }}>
                <div>
                  <input
                    type="text"
                    placeholder="Operator (e.g., APII, BFPME)"
                    value={filters.operator}
                    onChange={(e) => setFilters({ ...filters, operator: e.target.value })}
                    className="form-control"
                  />
                </div>
                <div>
                  <button
                    className="btn btn-secondary"
                    onClick={() => {
                      setSearchQuery('');
                      setFilters({ stage: '', type: '', operator: '' });
                    }}
                  >
                    Clear Filters
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="card" style={{ marginTop: '1.5rem' }}>
            <div className="card-header">
              <h2>Search Results ({filteredResources.length} resources found)</h2>
            </div>
            <div className="card-content">
              {filteredResources.length === 0 ? (
                <p className="text-center">No resources match your search criteria. Try adjusting your filters.</p>
              ) : (
                <div className="resources-list">
                  {filteredResources.map((resource) => (
                    <div className="resource-card" key={resource.id}>
                      <div className="resource-header">
                        <h3>{resource.name}</h3>
                        <span className="resource-type-badge">{resource.type.replace('_', ' ')}</span>
                      </div>
                      <p><strong>Operator:</strong> {resource.operator}</p>
                      <p>{resource.description}</p>
                      <div className="resource-meta" style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#666' }}>
                        <span><strong>Eligibility:</strong> {resource.eligibility_stages.join(', ')}</span>
                        <span className="meta-separator">|</span>
                        <span><strong>Domains:</strong> {resource.domains_addressed.join(', ')}</span>
                        <span className="meta-separator">|</span>
                        <span><strong>Relevance:</strong> {(resource.relevance_score * 100).toFixed(0)}%</span>
                      </div>
                      {resource.blockers_resolved && resource.blockers_resolved.length > 0 && (
                        <div className="resource-blockers" style={{ marginTop: '0.5rem' }}>
                          <small><strong>Addresses Blockers:</strong> {resource.blockers_resolved.join(', ')}</small>
                        </div>
                      )}
                      <div className="resource-footer" style={{ marginTop: '1rem', textAlign: 'right' }}>
                        <a
                          href={resource.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn btn-sm btn-secondary"
                        >
                          View Resource
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};