import React from "react";

export const HeaderSection = (): JSX.Element => {
  const signalBars = [
    { height: "h-[5px]", top: "top-[11px]" },
    { height: "h-2", top: "top-[7px]" },
    { height: "h-[11px]", top: "top-1" },
    { height: "h-3.5", top: "top-px" },
  ];

  return (
    <header className="w-full px-5 pt-[18px]">
      <div className="flex items-center justify-between h-[21px] text-white text-sm [font-family:'Poppins',Helvetica] font-normal tracking-[0] leading-[normal]">
        <time className="opacity-0 translate-y-[-1rem] animate-fade-in [--animation-delay:0ms]">
          11:11
        </time>
         
        <div className="flex items-center gap-2 opacity-0 translate-y-[-1rem] animate-fade-in [--animation-delay:100ms]">
          <div className="flex items-end gap-0.5 h-3.5 relative">
            {signalBars.map((bar, index) => (
              <div key={index} className={`relative ${bar.height}`}>
                <img
                  className={`absolute ${bar.top} left-0 w-0.5 ${bar.height}`}
                  alt="Signal bar"
                  src="https://c.animaapp.com/mh6k8iziKQgPTu/img/vector-1.svg"
                />
              </div>
            ))}
          </div>

          <span>4G</span>

          <img
            className="w-[23px] h-[11px]"
            alt="Battery"
            src="https://c.animaapp.com/mh6k8iziKQgPTu/img/vector-5.svg"
          />
        </div>
      </div>
    </header>
  );
};
