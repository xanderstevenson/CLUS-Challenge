import React, { useState, useEffect } from "react";
import styled from 'styled-components'

const Timer = styled.h3` {
    margin : 1rem;
    width: 100%;
    display: flex;
    height: 12%;
    justify-content: center;
    align-items: center;
}`

const StopWatch = () => {
  const [count, setCount] = useState(0);

  useEffect(() => {
      const timer = setTimeout(() => {
        setCount((prevCount) => prevCount + 1);
      }, 1000);

      return () => {
        clearTimeout(timer);
      };
  });

  return (
    <Timer>
        <h1>{count}s</h1>
    </Timer>
  );
}

export default StopWatch;