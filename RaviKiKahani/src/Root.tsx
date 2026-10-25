import React from "react";
import { Composition } from "remotion";
import { RaviKiKahani } from "./RaviKiKahani";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="RaviKiKahani"
        component={RaviKiKahani}
        durationInFrames={1800}
        fps={30}
        width={1080}
        height={1920}
      />
    </>
  );
};
