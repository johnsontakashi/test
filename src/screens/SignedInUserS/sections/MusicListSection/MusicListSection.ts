import React from "react";
import { Card, CardContent } from "../../../../components/ui/card";

export const MusicListSection = (): JSX.Element => {
  const musicData = {
    title: "Inspire",
    genre: "Pop",
    likes: 0,
    timestamp: "1 month ago",
  };

  return (
    <Card className="w-full rounded-[10px] backdrop-blur-[6px] backdrop-brightness-[100%] [-webkit-backdrop-filter:blur(6px)_brightness(100%)] [background:radial-gradient(50%_50%_at_0%_0%,rgba(0,0,0,0.6)_0%,rgba(0,0,0,0.45)_100%)] border-0">
      <CardContent className="p-0 h-[85px] flex items-center justify-between px-4">
        <div className="flex flex-col gap-[8px]">
          <div className="h-[17px] flex items-center justify-center [font-family:'Montserrat',Helvetica] font-semibold text-white text-sm tracking-[0] leading-[normal]">
            {musicData.title}
          </div>
          <div className="h-[17px] flex items-center justify-center [font-family:'Montserrat',Helvetica] font-normal text-white text-sm tracking-[0] leading-[normal]">
            {musicData.genre}
          </div>
        </div>

        <div className="flex flex-col gap-[8px] items-end">
          <div className="h-[17px] flex items-center justify-center [font-family:'Montserrat',Helvetica] font-normal text-transparent text-sm text-center tracking-[0] leading-[normal]">
            <span className="font-medium text-white">Likes: </span>
            <span className="font-medium text-[#61b15a]">
              {musicData.likes}
            </span>
          </div>
          <div className="h-[17px] flex items-center justify-center [font-family:'Montserrat',Helvetica] font-medium text-white text-sm text-center tracking-[0] leading-[normal]">
            {musicData.timestamp}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
