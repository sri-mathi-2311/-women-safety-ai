import { useEffect, useState } from 'react';
import './CustomCursor.css';

export default function CustomCursor() {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [clicked, setClicked] = useState(false);
  const [linkHovered, setLinkHovered] = useState(false);
  const [hidden, setHidden] = useState(false);

  useEffect(() => {
    const addEventListeners = () => {
      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseenter', onMouseEnter);
      document.addEventListener('mouseleave', onMouseLeave);
      document.addEventListener('mousedown', onMouseDown);
      document.addEventListener('mouseup', onMouseUp);
    };

    const removeEventListeners = () => {
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseenter', onMouseEnter);
      document.removeEventListener('mouseleave', onMouseLeave);
      document.removeEventListener('mousedown', onMouseDown);
      document.removeEventListener('mouseup', onMouseUp);
    };

    const onMouseMove = (e) => {
      setPosition({ x: e.clientX, y: e.clientY });
    };

    const onMouseDown = () => setClicked(true);
    const onMouseUp = () => setClicked(false);
    const onMouseLeave = () => setHidden(true);
    const onMouseEnter = () => setHidden(false);

    const handleLinkHoverEvents = () => {
      document.querySelectorAll('a, button, input, textarea, .clickable, select').forEach((el) => {
        el.removeEventListener('mouseover', handleHoverIn);
        el.removeEventListener('mouseout', handleHoverOut);
        
        el.addEventListener('mouseover', handleHoverIn);
        el.addEventListener('mouseout', handleHoverOut);
      });
    };

    const handleHoverIn = () => setLinkHovered(true);
    const handleHoverOut = () => setLinkHovered(false);

    // Initial setup
    addEventListeners();
    handleLinkHoverEvents();

    // Observe DOM changes to attach listeners to dynamic elements (e.g. navigation pages changing)
    const mutationObserver = new MutationObserver(() => {
      handleLinkHoverEvents();
    });
    mutationObserver.observe(document.body, { childList: true, subtree: true });

    return () => {
      removeEventListeners();
      mutationObserver.disconnect();
    };
  }, []);

  const cursorClasses = `custom-cursor ${clicked ? 'clicked' : ''} ${
    linkHovered ? 'hovered' : ''
  } ${hidden ? 'hidden' : ''}`;

  return (
    <>
      <div
        className={cursorClasses + " dot"}
        style={{ left: `${position.x}px`, top: `${position.y}px` }}
      />
      <div
        className={cursorClasses + " reticle"}
        style={{ left: `${position.x}px`, top: `${position.y}px` }}
      />
    </>
  );
}
