"use client";

import "@photo-sphere-viewer/core/index.css";
import { useEffect, useRef } from "react";

export default function PanoramaViewer({ src }: { src: string }) {
  const container = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let unmounted = false;
    let viewer: { destroy(): void } | undefined;
    import("@photo-sphere-viewer/core").then(({ Viewer }) => {
      if (!unmounted) viewer = new Viewer({ container: container.current!, panorama: src });
    });
    return () => {
      unmounted = true;
      viewer?.destroy();
    };
  }, [src]);

  return <div ref={container} className="panorama" />;
}
