"use client";

import "@photo-sphere-viewer/core/index.css";
import { useEffect, useRef } from "react";

const fitStripToHorizon = (image: HTMLImageElement) => ({
  fullWidth: image.width,
  fullHeight: Math.round(image.width / 2),
  croppedWidth: image.width,
  croppedHeight: image.height,
  croppedX: 0,
  croppedY: Math.round((image.width / 2 - image.height) / 2),
});

export default function PanoramaViewer({ src }: { src: string }) {
  const container = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let unmounted = false;
    let viewer: { destroy(): void } | undefined;
    import("@photo-sphere-viewer/core").then(({ Viewer }) => {
      if (!unmounted) viewer = new Viewer({ container: container.current!, panorama: src, panoData: fitStripToHorizon });
    });
    return () => {
      unmounted = true;
      viewer?.destroy();
    };
  }, [src]);

  return <div ref={container} className="panorama" />;
}
