import '@testing-library/jest-dom';

// Mock d3 for Jest environment (since d3 v7 is pure ESM)
jest.mock('d3', () => {
  const chainable = () => {
    const obj = {
      selectAll: () => obj,
      data: () => obj,
      join: () => obj,
      attr: () => obj,
      style: () => obj,
      remove: () => obj,
      append: () => obj,
      text: () => obj,
      on: () => obj,
      datum: () => obj,
      call: () => obj,
    };
    return obj;
  };

  const scale = () => {
    const fn = (x) => x;
    fn.domain = () => fn;
    fn.range = () => fn;
    return fn;
  };

  return {
    select: chainable,
    selectAll: chainable,
    scaleLinear: scale,
    scaleSequential: scale,
    interpolateViridis: () => '#000',
    line: () => {
      const fn = () => '';
      fn.x = () => fn;
      fn.y = () => fn;
      fn.curve = () => fn;
      return fn;
    },
    curveLinear: () => {},
    axisBottom: () => () => {},
    axisLeft: () => () => {},
  };
});

