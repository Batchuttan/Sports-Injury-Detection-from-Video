"use client";

import React from "react";

/**
 * SmoothScroll component
 *
 * Restores 100% native, responsive scrolling for:
 * 1. Laptop touchpads (two-finger scroll, gestures) at full normal speed
 * 2. Mouse scroll bar buttons, track clicks, and thumb dragging
 * 3. Physical mouse wheel scrolling with standard browser responsiveness
 */
export default function SmoothScroll({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
