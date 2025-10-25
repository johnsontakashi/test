import React from "react";
import { Card, CardContent } from "../../../../components/ui/card";

export const ProfileSection = (): JSX.Element => {
  const profileData = {
    artistName: "OMW",
    genre: "Pop",
    likes: 0,
    timestamp: "1 month ago",
  };

  return (
    <Card className="w-full rounded-[10px] backdrop-blur-[6px] backdrop-brightness-[100%] [-webkit-backdrop-filter:blur(6px)_brightness(100%)] [background:radial-gradient(50%_50%_at_0%_0%,rgba(0,0,0,0.6)_0%,rgba(0,0,0,0.45)_100%)] border-0 translate-y-[-1rem] animate-fade-in opacity-0 [--animation-delay:200ms]">
      <CardContent className="p-0">
        <div className="flex items-center justify-between px-4 py-[21px] h-[85px]">
          <div className="flex flex-col gap-3">
            <h2 className="h-[17px] flex items-center justify-center [font-family:'Montserrat',Helvetica] font-semibold text-white text-sm text-center tracking-[0] leading-[normal]">
              {profileData.artistName}
            </h2>
            <p className="h-[17px] flex items-center justify-center [font-family:'Montserrat',Helvetica] font-normal text-white text-sm text-center tracking-[0] leading-[normal]">
              {profileData.genre}
            </p>
          </div>

          <div className="flex flex-col gap-3">
            <div className="h-[17px] flex items-center justify-center [font-family:'Montserrat',Helvetica] font-normal text-transparent text-sm text-center tracking-[0] leading-[normal]">
              <span className="font-medium text-white">Likes: </span>
              <span className="font-medium text-[#61b15a]">
                {profileData.likes}
              </span>
            </div>
            <time className="h-[17px] flex items-center justify-center [font-family:'Montserrat',Helvetica] font-medium text-white text-sm text-center tracking-[0] leading-[normal]">
              {profileData.timestamp}
            </time>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
