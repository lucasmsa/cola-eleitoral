import { useId, useState } from 'react';

export function useDisclosure(initialOpen = false, onToggle?: (open: boolean) => void) {
  const [open, setOpen] = useState(initialOpen);
  const id = useId();
  return {
    open,
    panelId: `${id}-panel`,
    toggle: () => {
      const next = !open;
      setOpen(next);
      onToggle?.(next);
    },
  };
}
