import React, { useState } from 'react';
import { SIMULATION_PARAMETERS } from '../utils/constants';

const ControlPanel = ({ onRunSimulation, config, setConfig, loading, error }) => {
  const [formErrors, setFormErrors] = useState({});

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const newValue = type === 'checkbox' ? checked :
                    type === 'number' ? parseFloat(value) :
                    value;

    setConfig(prev => ({
      ...prev,
      [name]: newValue
    }));

    // Clear field-specific error
    if (formErrors[name]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const errors = {};

    // Validate that max_capacity >= init_energy
    if (config.max_capacity < config.init_energy) {
      errors.max_capacity = 'Max capacity must be greater than or equal to initial energy';
      errors.init_energy = 'Max capacity must be greater than or equal to initial energy';
    }

    // Validate that area is positive
    if (config.area <= 0) {
      errors.area = 'Area must be positive';
    }

    // Validate that nodes is positive
    if (config.nodes <= 0) {
      errors.nodes = 'Number of nodes must be positive';
    }

    // Validate that rounds is positive
    if (config.rounds <= 0) {
      errors.rounds = 'Number of rounds must be positive';
    }

    // Validate that cluster ratio is between 0 and 1
    if (config.cluster_ratio <= 0 || config.cluster_ratio > 1) {
      errors.cluster_ratio = 'Cluster ratio must be between 0 and 1';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onRunSimulation(config);
    }
  };

  return (
    <div className="control-panel">
      <h2>Simulation Parameters</h2>
      <form onSubmit={handleSubmit}>
        {SIMULATION_PARAMETERS.map(param => {
          const ParamComponent = () => {
            switch (param.type) {
              case 'number':
                return (
                  <div key={param.name} className={`form-group ${formErrors[param.name] ? 'error' : ''}`}>
                    <label htmlFor={param.name}>
                      {param.label}
                      {param.explanation && (
                        <span className="explanation" title={param.explanation}>
                          ℹ️
                        </span>
                      )}
                    </label>
                    <div className="input-wrapper">
                      <input
                        id={param.name}
                        type="number"
                        name={param.name}
                        min={param.min}
                        max={param.max}
                        step={param.step}
                        value={config[param.name] || param.default}
                        onChange={handleChange}
                        className="input-field"
                      />
                      <span className="unit">{param.unit}</span>
                    </div>
                    {formErrors[param.name] && (
                      <span className="error-message">{formErrors[param.name]}</span>
                    )}
                  </div>
                );
              case 'select':
                return (
                  <div key={param.name} className={`form-group ${formErrors[param.name] ? 'error' : ''}`}>
                    <label htmlFor={param.name}>
                      {param.label}
                      {param.explanation && (
                        <span className="explanation" title={param.explanation}>
                          ℹ️
                        </span>
                      )}
                    </label>
                    <select
                      id={param.name}
                      name={param.name}
                      value={config[param.name] || param.default}
                      onChange={handleChange}
                      className="input-field"
                    >
                      {param.options.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                    {formErrors[param.name] && (
                      <span className="error-message">{formErrors[param.name]}</span>
                    )}
                  </div>
                );
              case 'checkbox':
                return (
                  <div key={param.name} className={`form-group ${formErrors[param.name] ? 'error' : ''}`}>
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        name={param.name}
                        checked={config[param.name] || param.default}
                        onChange={handleChange}
                        className="checkbox-input"
                      />
                      <span>
                        {param.label}
                        {param.explanation && (
                          <span className="explanation" title={param.explanation}>
                            ℹ️
                          </span>
                        )}
                      </span>
                    </label>
                    {formErrors[param.name] && (
                      <span className="error-message">{formErrors[param.name]}</span>
                    )}
                  </div>
                );
              default:
                return null;
            }
          };
          return <ParamComponent />;
        })}

        <div className="form-actions">
          <button
            type="submit"
            disabled={loading}
            className="run-button"
          >
            {loading ? 'Running...' : 'Run Simulation'}
          </button>
          <button
            type="button"
            onClick={() => setConfig(() => {
              const newConfig = {};
              SIMULATION_PARAMETERS.forEach(p => {
                newConfig[p.name] = p.default;
              });
              return newConfig;
            })}
            className="reset-button"
          >
            Reset to Defaults
          </button>
        </div>

        {error && (
          <div className="form-error">
            <strong>Error:</strong> {error}
          </div>
        )}
      </form>
    </div>
  );
};

export default ControlPanel;