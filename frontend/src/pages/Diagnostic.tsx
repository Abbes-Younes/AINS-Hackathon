import React, { useState } from 'react';

export const Diagnostic = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [answers, setAnswers] = useState<any>({});

  const steps = [
    { id: 1, title: 'Entrepreneur Profile', description: 'Basic information about you and your venture' },
    { id: 2, title: 'Sector Specific Questions', description: 'Questions tailored to your industry/sector' },
    { id: 3, title: 'Maturity Assessment', description: 'Questions to determine your current stage' },
    { id: 4, title: 'Validation & Evidence', description: 'Questions about your traction and validation efforts' },
    { id: 5, title: 'Review & Submit', description: 'Review your answers and complete the diagnostic' }
  ];

  const handleNext = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = () => {
    // In a real app, this would submit answers to the backend
    console.log('Diagnostic submitted:', answers);
    alert('Diagnostic completed! Results would be processed and you would be redirected to see your results.');
  };

  return (
    <div className="app">
      <div className="main-content">
        <div className="container">
          <h1>Entrepreneur Diagnostic</h1>
          <p className="text-muted">Step {currentStep} of {steps.length}</p>

          <div className="card">
            <div className="card-header">
              <h2>{steps[currentStep - 1].title}</h2>
              <p className="text-muted">{steps[currentStep - 1].description}</p>
            </div>

            <div className="card-content">
              {/* Step-specific content would go here */}
              <div className="step-content">
                {currentStep === 1 && (
                  <>
                    <div className="form-group">
                      <label>Full Name</label>
                      <input type="text" className="form-control" placeholder="Enter your full name" />
                    </div>
                    <div className="form-group">
                      <label>Email Address</label>
                      <input type="email" className="form-control" placeholder="Enter your email" />
                    </div>
                    <div className="form-group">
                      <label>Phone Number</label>
                      <input type="tel" className="form-control" placeholder="Enter your phone number" />
                    </div>
                    <div className="form-group">
                      <label>Venture Name</label>
                      <input type="text" className="form-control" placeholder="Enter your venture/business name" />
                    </div>
                    <div className="form-group">
                      <label>Sector</label>
                      <select className="form-control">
                        <option value="">Select your sector</option>
                        <option value="technology">Technology</option>
                        <option value="agri-food">Agri-food</option>
                        <option value="artisanat">Artisanat</option>
                        <option value="services">Services</option>
                        <option value="manufacturing">Manufacturing</option>
                      </select>
                    </div>
                  </>
                )}
                {currentStep === 2 && (
                  <>
                    <p>Based on your selected sector, here are some specific questions:</p>
                    <div className="form-group">
                      <label>Year of Establishment</label>
                      <input type="number" className="form-control" placeholder="When was your venture established?" />
                    </div>
                    <div className="form-group">
                      <label>Number of Employees (including founders)</label>
                      <input type="number" className="form-control" placeholder="How many people work in your venture?" />
                    </div>
                    <div className="form-group">
                      <label>Monthly Revenue (in TND)</label>
                      <input type="number" className="form-control" placeholder="What is your average monthly revenue?" />
                    </div>
                  </>
                )}
                {currentStep === 3 && (
                  <>
                    <p>These questions help determine your current maturity stage:</p>
                    <div className="form-group">
                      <label>Do you have a registered legal entity (SARL, SA, etc.)?</label>
                      <select className="form-control">
                        <option value="">Select...</option>
                        <option value="yes">Yes</option>
                        <option value="no">No</option>
                        <option value="in_process">In process</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Have you validated your business model with paying customers?</label>
                      <select className="form-control">
                        <option value="">Select...</option>
                        <option value="yes">Yes, with paying customers</option>
                        <option value="interviews">Yes, through customer interviews only</option>
                        <option value="no">No validation yet</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Do you have a written business plan?</label>
                      <select className="form-control">
                        <option value="">Select...</option>
                        <option value="yes">Yes, detailed plan</option>
                        <option value="outline">Yes, basic outline</option>
                        <option value="no">No written plan</option>
                      </select>
                    </div>
                  </>
                )}
                {currentStep === 4 && (
                  <>
                    <p>Let's understand your validation and evidence:</p>
                    <div className="form-group">
                      <label>How many customer interviews have you conducted?</label>
                      <input type="number" className="form-control" placeholder="Number of interviews" />
                    </div>
                    <div className="form-group">
                      <label>Do you have documented customer feedback or testimonials?</label>
                      <select className="form-control">
                        <option value="">Select...</option>
                        <option value="yes">Yes, documented</option>
                        <option value="some">Some, informal</option>
                        <option value="no">No documented feedback</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Have you generated any revenue to date?</label>
                      <select className="form-control">
                        <option value="">Select...</option>
                        <option value="yes">Yes, revenue generated</option>
                        <option value="pending">Yes, pending/invoiced</option>
                        <option value="no">No revenue yet</option>
                      </select>
                    </div>
                  </>
                )}
                {currentStep === 5 && (
                  <>
                    <h3>Review Your Answers</h3>
                    <p>Please review your answers before submitting the diagnostic:</p>
                    <div className="card" style={{ padding: '1rem', backgroundColor: '#f8f9fa' }}>
                      <p><strong>Profile Information:</strong></p>
                      <p>Name: [User Input]</p>
                      <p>Email: [User Input]</p>
                      <p>Venture: [User Input]</p>
                      <p>Sector: [User Input]</p>
                    </div>
                    <div className="card" style={{ padding: '1rem', backgroundColor: '#f8f9fa', marginTop: '1rem' }}>
                      <p><strong>Assessment Responses:</strong></p>
                      <p>Legal Entity: [User Input]</p>
                      <p>Customer Validation: [User Input]</p>
                      <p>Business Plan: [User Input]</p>
                      <p>Revenue Status: [User Input]</p>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>

          <div className="card-footer" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <button
              className="btn btn-secondary"
              onClick={handlePrev}
              disabled={currentStep === 1}
            >
              Previous Step
            </button>
            <button
              className="btn btn-primary"
              onClick={currentStep < steps.length ? handleNext : handleSubmit}
            >
              {currentStep < steps.length ? 'Next Step' : 'Complete Diagnostic'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};