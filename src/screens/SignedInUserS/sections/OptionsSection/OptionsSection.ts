import React from "react";
import { Card, CardContent } from "../../../../components/ui/card";

export const OptionsSection = (): JSX.Element => {
  const trackData = {
    title: "I Got Me",
    genre: "Pop",
    likes: 0,
    timestamp: "1 month ago",
  };

  return (
    <section className="w-full px-[15px] opacity-0 translate-y-[-1rem] animate-fade-in [--animation-delay:200ms]">
      <Card className="rounded-[10px] backdrop-blur-[6px] backdrop-brightness-[100%] [-webkit-backdrop-filter:blur(6px)_brightness(100%)] [background:radial-gradient(50%_50%_at_0%_0%,rgba(0,0,0,0.6)_0%,rgba(0,0,0,0.45)_100%)] border-0">
        <CardContent className="p-0 py-[21px]">
          <div className="grid grid-cols-2 gap-4 px-4">
            <div className="flex flex-col gap-3">
              <div className="h-[17px] flex items-center justify-start [font-family:'Montserrat',Helvetica] font-semibold text-white text-sm tracking-[0] leading-[normal]">
                {trackData.title}
              </div>
              <div className="h-[17px] flex items-center justify-start [font-family:'Montserrat',Helvetica] font-normal text-white text-sm tracking-[0] leading-[normal]">
                {trackData.genre}
              </div>
            </div>
            <div className="flex flex-col gap-3">
              <div className="h-[17px] flex items-center justify-end [font-family:'Montserrat',Helvetica] font-normal text-transparent text-sm tracking-[0] leading-[normal]">
                <span className="font-medium text-white">Likes: </span>
                <span className="font-medium text-[#61b15a]">
                  {trackData.likes}
                </span>
              </div>
              <div className="h-[17px] flex items-center justify-end [font-family:'Montserrat',Helvetica] font-medium text-white text-sm tracking-[0] leading-[normal]">
                {trackData.timestamp}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </section>
  );
};
