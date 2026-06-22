# AINS Entrepreneurial Orientation Engine - Frontend

This is the frontend dashboard for the Intelligent Entrepreneurial Orientation Engine, built with React and TypeScript.

## Features

- **Dashboard**: Overview of diagnostic results, scores, blockers, recommended actions, and roadmap
- **Diagnostic**: Step-by-step entrepreneurial assessment questionnaire
- **Scoring**: Detailed view of entrepreneurial scores with breakdown and history
- **Roadmap**: Personalized, sequenced action plan organized by time horizons
- **Resources**: Searchable database of Tunisian entrepreneurship support programs
- **Assistant**: Grounded conversational assistant that provides guidance based on your profile

## Technology Stack

- **Framework**: React 18 with TypeScript
- **Styling**: Custom CSS with responsive design
- **State Management**: React Query for server state, React Context for authentication
- **Routing**: React Router v6
- **UI Components**: Custom built (no external UI library dependency for core components)
- **Build Tool**: Vite for fast development and building

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

### Development

To start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

### Production Build

To create a production build:
```bash
npm run build
```

To preview the production build:
```bash
npm run preview
```

## Project Structure

```
frontend/
├── public/
├── src/
│   ├── components/     # Reusable UI components
│   ├── context/        # React contexts (Auth)
│   ├── pages/          # Page components
│   ├── App.tsx         # Main application component
│   ├── main.tsx        # Entry point
│   └── index.css       # Global styles
├── vite.config.ts      # Vite configuration
├── tsconfig.json       # TypeScript configuration
└── package.json        # Dependencies and scripts
```

## Components

### Layout Components
- `Header`: Application header with user info and actions
- `Sidebar`: Navigation menu for different sections

### Dashboard Components
- `DiagnosticPanel`: Summary of diagnostic results and stage
- `ScoresOverview`: Visual representation of entrepreneurial scores
- `PriorityBlockers`: Identified blockers with priority levels
- `RecommendedActions`: Suggested actions with linked resources
- `RoadmapOverview`: Timeline view of the personalized roadmap
- `MonParcoursView`: Longitudinal tracking of entrepreneurial journey

### Page Components
- `Dashboard`: Main overview page
- `Diagnostic`: Interactive questionnaire for assessment
- `Scoring`: Detailed score breakdown and history
- `Roadmap`: Complete roadmap with time horizon organization
- `Resources`: Searchable database of support programs
- `Assistant`: Conversational assistant for personalized guidance

## Design Principles

1. **Responsive Design**: Works on desktop and mobile devices
2. **Clear Visual Hierarchy**: Important information is prominently displayed
3. **Consistent Styling**: Unified color scheme and typography
4. **User-Friendly**: Intuitive navigation and interactions
5. **Accessibility**: Proper color contrast and interactive elements

## API Integration

The frontend is designed to communicate with the backend API endpoints:
- Diagnostic: `/api/diagnostic/*`
- Scoring: `/api/scoring/*`
- Roadmap: `/api/roadmap/*`
- Resources: `/api/resources/*`
- Assistant: `/api/assistant/*`

In the current implementation, the frontend uses mock data and simulates API calls. For integration with the actual backend, the service calls would need to be updated to point to the actual API endpoints.

## Customization

To customize the application for different use cases:

1. **Styling**: Modify `src/index.css` to change colors, spacing, or typography
2. **Content**: Update the mock data in the page components to reflect real data
3. **Functionality**: Enhance the components with additional features as needed
4. **Integration**: Replace the mock API calls with actual service calls to the backend

## Browser Support

The application supports modern browsers that support ES6+ features:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

This project is part of the AINS Hackathon 2026.