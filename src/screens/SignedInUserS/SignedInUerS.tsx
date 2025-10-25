import { EyeIcon, HeartIcon, UserIcon } from "lucide-react";
import React from "react";
import { Button } from "../../components/ui/button";
import { HeaderSection } from "./sections/HeaderSection";
import { MusicListSection } from "./sections/MusicListSection";
import { OptionsSection } from "./sections/OptionsSection";
import { ProfileSection } from "./sections/ProfileSection";
import { UploadSection } from "./sections/UploadSection";

export const SignedInUserS = (): JSX.Element => {
  const navigationItems = [
    { label: "Likes", icon: HeartIcon, active: false },
    { label: "Discover", icon: EyeIcon, active: false },
    { label: "Profile", icon: UserIcon, active: true },
  ];

  return (
    <div
      className="bg-[#191919] overflow-hidden w-full min-w-[414px] relative flex flex-col"
      data-model-id="141:332"
    >
      <div className="relative flex-1 flex flex-col">
        <img
          className="absolute inset-0 w-full h-full object-cover rounded-b-[10px]"
          alt="Background"
          src="https://c.animaapp.com/mh6k8iziKQgPTu/img/rectangle-242.png"
        />

        <div className="absolute inset-0 rounded-b-[10px] backdrop-blur-[1.5px] backdrop-brightness-[100%] [-webkit-backdrop-filter:blur(1.5px)_brightness(100%)] [background:radial-gradient(50%_50%_at_0%_0%,rgba(0,0,0,0.2)_0%,rgba(0,0,0,0.15)_100%)]" />

        <div className="relative z-10 flex flex-col">
          <HeaderSection />

          <div className="px-[77px] mt-3 translate-y-[-1rem] animate-fade-in opacity-0 [--animation-delay:200ms]">
            <div className="w-full rounded-[10px] backdrop-blur-[6px] backdrop-brightness-[100%] [-webkit-backdrop-filter:blur(6px)_brightness(100%)] [background:radial-gradient(50%_50%_at_0%_0%,rgba(0,0,0,0.8)_0%,rgba(0,0,0,0.6)_100%)] py-[18px] px-4">
              <h1 className="[font-family:'Montserrat',Helvetica] font-semibold text-white text-lg text-center tracking-[0] leading-[normal]">
                Jane &amp; The Boy
              </h1>
            </div>
          </div>

          <div className="flex gap-[27px] px-[15px] mt-[262px] translate-y-[-1rem] animate-fade-in opacity-0 [--animation-delay:400ms]">
            <Button className="flex-1 bg-[#61b15a] hover:bg-[#61b15a]/90 rounded-[30px] h-[41px] transition-colors">
              <span className="[font-family:'Montserrat',Helvetica] font-semibold text-white text-[15px] tracking-[0] leading-[normal]">
                Options
              </span>
            </Button>
            <Button className="flex-1 bg-[#61b15a] hover:bg-[#61b15a]/90 rounded-[30px] h-[41px] transition-colors">
              <span className="[font-family:'Montserrat',Helvetica] font-semibold text-white text-[15px] tracking-[0] leading-[normal]">
                Upload
              </span>
            </Button>
          </div>

          <div className="mt-8 translate-y-[-1rem] animate-fade-in opacity-0 [--animation-delay:600ms]">
            <UploadSection />
          </div>

          <div className="translate-y-[-1rem] animate-fade-in opacity-0 [--animation-delay:800ms]">
            <OptionsSection />
          </div>

          <div className="translate-y-[-1rem] animate-fade-in opacity-0 [--animation-delay:1000ms]">
            <ProfileSection />
          </div>

          <div className="translate-y-[-1rem] animate-fade-in opacity-0 [--animation-delay:1200ms]">
            <MusicListSection />
          </div>
        </div>
      </div>

      <nav className="relative z-20 w-full bg-[#191919] shadow-[4px_4px_40px_#ffffff26] py-4">
        <div className="flex items-center justify-around px-4">
          {navigationItems.map((item, index) => (
            <button
              key={index}
              className="flex flex-col items-center gap-1 transition-colors hover:opacity-80"
            >
              <item.icon
                className={`w-5 h-5 ${
                  item.active ? "text-[#61b15a]" : "text-white"
                }`}
              />
              <span
                className={`[font-family:'Montserrat',Helvetica] font-normal text-xs tracking-[0] leading-[normal] ${
                  item.active ? "text-[#61b15a]" : "text-white"
                }`}
              >
                {item.label}
              </span>
            </button>
          ))}
        </div>
      </nav>
    </div>
  );
};
