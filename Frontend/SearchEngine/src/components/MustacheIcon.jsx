// src/components/MustacheIcon.js
import React from 'react';

export function MustacheIcon({ className, onClick }) {
    return (
        <svg
            viewBox="0 0 512 512"
            fill="currentColor"
            className={`cursor-pointer transform transition-transform hover:scale-110 ${className}`} // added cursor and hover effects
            xmlns="http://www.w3.org/2000/svg"
            onClick={onClick} // Add click event handler
        >
            <g transform="translate(0.000000,512.000000) scale(0.100000,-0.100000)"
                fill="currentColor" stroke="none">
                <path d="M2073 4945 c-372 -67 -662 -338 -765 -714 -19 -68 -22 -113 -27 -407
                    l-6 -331 -44 -34 c-91 -70 -130 -190 -97 -304 14 -45 29 -69 70 -110 64 -64
                    122 -85 238 -85 l78 0 0 -37 c0 -64 28 -214 54 -292 88 -257 280 -478 524
                    -600 l62 -31 0 -139 0 -138 -95 -63 -95 -63 -303 -52 c-166 -29 -328 -62 -359
                    -74 -115 -44 -231 -151 -287 -267 -57 -114 -61 -150 -61 -592 l0 -403 25 -24
                    c29 -30 74 -32 106 -6 l24 19 5 424 c5 414 6 424 28 481 32 79 116 168 195
                    207 51 24 110 37 336 75 150 25 275 44 276 43 2 -2 53 -103 114 -225 63 -127
                    119 -227 130 -233 48 -25 70 -14 177 92 l104 102 0 -478 0 -477 25 -24 c32
                    -33 78 -33 110 0 l25 24 0 477 0 478 104 -102 c107 -106 129 -117 177 -92 11
                    6 67 106 130 233 61 122 112 223 114 225 1 1 126 -18 276 -43 226 -38 285 -51
                    336 -75 79 -39 163 -128 195 -207 22 -57 23 -68 28 -481 l5 -424 24 -19 c32
                    -26 77 -24 106 6 l25 24 0 398 c0 442 -5 484 -62 601 -47 95 -152 199 -249
                    245 -84 40 -98 43 -444 101 l-254 43 -95 63 -96 63 0 138 0 138 73 37 c98 50
                    148 85 235 168 95 90 159 174 215 284 66 129 117 317 117 435 l0 35 98 4 c80
                    3 106 9 147 30 101 52 149 133 150 248 0 66 -4 82 -31 130 -17 30 -51 70 -75
                    89 l-44 34 -6 331 c-5 294 -8 339 -27 407 -50 183 -129 319 -261 449 -143 143
                    -313 231 -508 265 -114 20 -860 20 -970 0z m-52 -1089 c150 -66 299 -90 544
                    -90 224 1 331 17 492 74 48 17 95 34 104 36 12 4 47 -50 148 -228 l132 -233
                    -4 -300 c-3 -268 -6 -308 -25 -375 -111 -394 -458 -662 -856 -660 -420 2 -789
                    313 -861 725 -11 64 -15 160 -15 350 l0 262 131 231 c72 128 137 232 144 232
                    7 0 37 -11 66 -24z m-501 -617 l0 -121 -85 3 c-80 4 -86 6 -117 37 -28 28 -33
                    39 -33 81 0 39 5 55 25 76 34 37 54 44 138 44 l72 1 0 -121z m2282 83 c28 -28
                    33 -39 33 -82 0 -43 -5 -54 -33 -82 -31 -31 -37 -33 -117 -37 l-85 -3 0 122 0
                    122 85 -3 c80 -4 86 -6 117 -37z m-1345 -1395 c99 -11 275 -1 326 19 15 6 17
                    -4 17 -113 l0 -118 -120 -120 -120 -120 -120 120 -120 120 0 118 c0 109 2 119
                    17 113 10 -4 64 -12 120 -19z"/>
                <path d="M2000 3427 c-49 -16 -133 -102 -148 -153 -19 -64 -15 -102 13 -129
                    49 -50 135 -15 135 55 0 41 39 80 80 80 41 0 80 -39 80 -80 0 -41 39 -80 80
                    -80 42 0 80 39 80 81 0 62 -23 113 -75 164 -70 71 -152 91 -245 62z"/>
                <path d="M2960 3427 c-49 -16 -133 -102 -148 -153 -19 -64 -15 -102 13 -129
                    49 -50 135 -15 135 55 0 41 39 80 80 80 41 0 80 -39 80 -80 0 -41 39 -80 80
                    -80 42 0 80 39 80 81 0 62 -23 113 -75 164 -70 71 -152 91 -245 62z"/>
                <path d="M2245 2791 c-131 -33 -230 -148 -242 -283 -5 -51 -3 -59 21 -83 l27
                    -27 172 4 c161 3 175 5 227 29 30 14 67 38 83 52 l27 26 28 -26 c15 -14 52
                    -38 82 -52 52 -24 66 -26 227 -29 l172 -4 27 27 c25 25 26 31 20 87 -11 112
                    -79 207 -186 260 -43 22 -55 23 -350 25 -168 1 -318 -2 -335 -6z"/>
            </g>
        </svg>
    );
}