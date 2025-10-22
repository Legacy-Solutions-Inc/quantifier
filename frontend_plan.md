# Next.js Frontend Architecture Plan

## 🎯 Frontend Overview

A modern React-based web application built with Next.js 14, providing an intuitive interface for the RSB Combinator API.

## 🏗️ Technology Stack

### Core Framework
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Shadcn/ui**: Modern component library

### State Management
- **Zustand**: Lightweight state management
- **React Query**: Server state management and caching
- **React Hook Form**: Form handling with validation

### Authentication
- **Supabase Auth**: Client-side authentication
- **NextAuth.js**: Optional additional auth layer

### Data Visualization
- **Recharts**: Charts and graphs for results
- **React Table**: Data tables for results display
- **React Dropzone**: File upload interface

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── (auth)/            # Auth route group
│   │   ├── login/         # Login page
│   │   └── register/      # Registration page
│   ├── dashboard/         # Main dashboard
│   ├── projects/          # Project management
│   ├── calculations/      # Calculation interface
│   ├── files/            # File management
│   └── layout.tsx        # Root layout
├── components/           # Reusable components
│   ├── ui/              # Base UI components
│   ├── forms/           # Form components
│   ├── charts/          # Data visualization
│   └── layout/          # Layout components
├── lib/                 # Utilities and configurations
│   ├── api/            # API client functions
│   ├── auth/           # Authentication utilities
│   ├── utils/          # Helper functions
│   └── validations/    # Form validation schemas
├── hooks/              # Custom React hooks
├── store/              # Zustand stores
├── types/              # TypeScript type definitions
└── styles/             # Global styles
```

## 🎨 UI/UX Design

### Design System
- **Color Palette**: Professional blue/gray theme
- **Typography**: Inter font family
- **Spacing**: 8px grid system
- **Components**: Consistent, accessible components

### Key Pages

#### 1. Dashboard
- Project overview cards
- Recent calculations
- Quick stats and metrics
- File upload area

#### 2. Project Management
- Project list with search/filter
- Create/edit project forms
- Project statistics
- File attachments

#### 3. Calculation Interface
- Step-by-step wizard
- File upload with validation
- Parameter configuration
- Real-time progress tracking
- Results visualization

#### 4. Results Display
- Interactive data tables
- Waste percentage charts
- Export options
- Comparison tools

## 🔧 Core Features

### 1. Authentication Flow
```typescript
// Login component
const LoginForm = () => {
  const { signIn } = useAuth();
  const [formData, setFormData] = useState({ email: '', password: '' });
  
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    await signIn(formData);
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  );
};
```

### 2. File Upload with Validation
```typescript
// File upload component
const FileUpload = ({ onFileSelect }: { onFileSelect: (file: File) => void }) => {
  const { uploadFile, validateFile } = useFiles();
  
  const handleDrop = async (files: File[]) => {
    const file = files[0];
    const validation = await validateFile(file);
    
    if (validation.valid) {
      onFileSelect(file);
    } else {
      showError(validation.errors.join(', '));
    }
  };
  
  return (
    <Dropzone onDrop={handleDrop} accept={{ 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'] }}>
      {/* Dropzone UI */}
    </Dropzone>
  );
};
```

### 3. Calculation Wizard
```typescript
// Multi-step calculation form
const CalculationWizard = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState<CalculationFormData>({});
  
  const steps = [
    { title: 'Upload Data', component: FileUploadStep },
    { title: 'Configure Parameters', component: ParametersStep },
    { title: 'Review & Run', component: ReviewStep },
    { title: 'Results', component: ResultsStep }
  ];
  
  return (
    <div className="wizard-container">
      <WizardSteps currentStep={step} steps={steps} />
      {steps[step - 1].component}
    </div>
  );
};
```

### 4. Results Visualization
```typescript
// Results display component
const ResultsDisplay = ({ results }: { results: CalculationResults }) => {
  return (
    <div className="results-container">
      <div className="summary-cards">
        <MetricCard title="Waste Percentage" value={`${results.wastePercentage}%`} />
        <MetricCard title="Total Weight" value={`${results.totalWeight} kg`} />
        <MetricCard title="Commercial Pieces" value={results.commercialPieces} />
      </div>
      
      <div className="results-table">
        <DataTable data={results.combinations} columns={columns} />
      </div>
      
      <div className="charts">
        <WasteChart data={results.wasteBreakdown} />
        <EfficiencyChart data={results.efficiencyData} />
      </div>
    </div>
  );
};
```

## 🔌 API Integration

### API Client Setup
```typescript
// lib/api/client.ts
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export const apiClient = {
  auth: {
    signIn: async (credentials: LoginCredentials) => {
      const { data, error } = await supabase.auth.signInWithPassword(credentials);
      return { data, error };
    },
    signUp: async (userData: RegisterData) => {
      const { data, error } = await supabase.auth.signUp(userData);
      return { data, error };
    }
  },
  
  calculations: {
    create: async (data: CalculationRequest) => {
      const response = await fetch('/api/calculations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      return response.json();
    },
    
    get: async (id: string) => {
      const response = await fetch(`/api/calculations/${id}`);
      return response.json();
    }
  }
};
```

### React Query Integration
```typescript
// hooks/useCalculations.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export const useCalculations = (projectId?: string) => {
  return useQuery({
    queryKey: ['calculations', projectId],
    queryFn: () => apiClient.calculations.list(projectId),
    enabled: !!projectId
  });
};

export const useCreateCalculation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: apiClient.calculations.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calculations'] });
    }
  });
};
```

## 🎨 Component Library

### Base Components
```typescript
// components/ui/Button.tsx
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({ 
  variant = 'primary', 
  size = 'md', 
  loading = false,
  children,
  ...props 
}) => {
  return (
    <button 
      className={cn(buttonVariants({ variant, size }), loading && 'opacity-50')}
      disabled={loading}
      {...props}
    >
      {loading && <Spinner className="mr-2" />}
      {children}
    </button>
  );
};
```

### Form Components
```typescript
// components/forms/CalculationForm.tsx
export const CalculationForm = () => {
  const { register, handleSubmit, formState: { errors } } = useForm<CalculationFormData>();
  const { mutate: createCalculation, isLoading } = useCreateCalculation();
  
  const onSubmit = (data: CalculationFormData) => {
    createCalculation(data);
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <FormField
        label="Target Lengths"
        error={errors.targetLengths?.message}
      >
        <Input {...register('targetLengths', { required: 'Target lengths are required' })} />
      </FormField>
      
      <Button type="submit" loading={isLoading}>
        Run Calculation
      </Button>
    </form>
  );
};
```

## 📱 Responsive Design

### Mobile-First Approach
```css
/* Tailwind responsive classes */
.results-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4;
}

.calculation-wizard {
  @apply w-full max-w-4xl mx-auto p-4 md:p-6 lg:p-8;
}

.data-table {
  @apply overflow-x-auto;
}
```

### Breakpoints
- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px+

## 🚀 Performance Optimizations

### Code Splitting
```typescript
// Lazy load heavy components
const ResultsVisualization = lazy(() => import('./ResultsVisualization'));
const FileUpload = lazy(() => import('./FileUpload'));

// Route-based splitting
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Projects = lazy(() => import('./pages/Projects'));
```

### Caching Strategy
```typescript
// React Query configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    },
  },
});
```

## 🔒 Security Features

### Authentication Guards
```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token');
  
  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
}

export const config = {
  matcher: ['/dashboard/:path*', '/projects/:path*', '/calculations/:path*']
};
```

### Input Validation
```typescript
// lib/validations/calculation.ts
import { z } from 'zod';

export const calculationSchema = z.object({
  targetLengths: z.array(z.number().positive()).min(1),
  rebarData: z.array(z.object({
    length: z.number().positive(),
    pieces: z.number().int().min(0),
    diameter: z.number().positive()
  })).min(1),
  tolerance: z.number().min(0).max(1).default(0.1)
});
```

## 🧪 Testing Strategy

### Unit Tests
```typescript
// __tests__/components/Button.test.tsx
import { render, screen } from '@testing-library/react';
import { Button } from '@/components/ui/Button';

describe('Button', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });
  
  it('shows loading state', () => {
    render(<Button loading>Loading</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

### Integration Tests
```typescript
// __tests__/pages/calculations.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { CalculationPage } from '@/app/calculations/page';

describe('Calculation Page', () => {
  it('displays calculation form', async () => {
    render(
      <QueryClientProvider client={new QueryClient()}>
        <CalculationPage />
      </QueryClientProvider>
    );
    
    await waitFor(() => {
      expect(screen.getByText('Run Calculation')).toBeInTheDocument();
    });
  });
});
```

## 📦 Deployment

### Vercel Deployment
```json
// vercel.json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "env": {
    "NEXT_PUBLIC_SUPABASE_URL": "@supabase-url",
    "NEXT_PUBLIC_SUPABASE_ANON_KEY": "@supabase-anon-key"
  }
}
```

### Docker Configuration
```dockerfile
# Dockerfile
FROM node:18-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM base AS build
RUN npm ci
COPY . .
RUN npm run build

FROM base AS runtime
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
EXPOSE 3000
CMD ["npm", "start"]
```

## 🎯 Key Features Implementation

### 1. Real-time Updates
```typescript
// hooks/useCalculationStatus.ts
export const useCalculationStatus = (calculationId: string) => {
  return useQuery({
    queryKey: ['calculation-status', calculationId],
    queryFn: () => apiClient.calculations.getStatus(calculationId),
    refetchInterval: (data) => data?.status === 'processing' ? 2000 : false
  });
};
```

### 2. File Drag & Drop
```typescript
// components/FileUpload.tsx
export const FileUpload = () => {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/csv': ['.csv']
    },
    onDrop: handleFileDrop
  });
  
  return (
    <div {...getRootProps()} className={cn(
      'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer',
      isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
    )}>
      <input {...getInputProps()} />
      {isDragActive ? 'Drop files here' : 'Drag & drop files or click to browse'}
    </div>
  );
};
```

### 3. Results Export
```typescript
// components/ExportButton.tsx
export const ExportButton = ({ calculationId }: { calculationId: string }) => {
  const { mutate: exportResults, isLoading } = useExportCalculation();
  
  const handleExport = (format: 'excel' | 'csv' | 'json') => {
    exportResults({ calculationId, format });
  };
  
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline">
          <Download className="mr-2 h-4 w-4" />
          Export
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem onClick={() => handleExport('excel')}>
          Export as Excel
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleExport('csv')}>
          Export as CSV
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleExport('json')}>
          Export as JSON
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
```

This comprehensive frontend architecture provides a modern, scalable, and user-friendly interface for the RSB Combinator web application, seamlessly integrating with the FastAPI backend and Supabase infrastructure.
