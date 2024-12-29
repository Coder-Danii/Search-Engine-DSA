// import React from 'react';
// import { X } from 'lucide-react';

// export function DocumentPreview({ document, onClose }) {
//   if (!document) return null;

//   return (
//     <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
//       <div className="bg-white dark:bg-brown-800 rounded-lg p-6 max-w-2xl w-full mx-4 relative max-h-[80vh] overflow-y-auto">
//         <button
//           onClick={onClose}
//           className="absolute top-2 right-2 text-gray-500 hover:text-gray-700"
//         >
//           <X size={20} />
//         </button>
        
//         <h2 className="text-xl font-bold mb-4 text-brown-800 dark:text-beige-100">
//           {document.title}
//         </h2>
        
//         <div className="space-y-4">
//           {document.preview && (
//             <div className="bg-brown-50 dark:bg-brown-700 p-4 rounded-lg">
//               <p className="text-brown-800 dark:text-beige-100">{document.preview}</p>
//             </div>
//           )}
          
//           <div className="flex flex-wrap gap-2">
//             {document.tags?.map((tag, index) => (
//               <span
//                 key={index}
//                 className="px-2 py-1 text-sm rounded-full bg-brown-100 dark:bg-brown-600 text-brown-800 dark:text-beige-100"
//               >
//                 {tag}
//               </span>
//             ))}
//           </div>
          
//           <div className="text-sm text-brown-600 dark:text-beige-300">
//             Last modified: {new Date(document.date).toLocaleDateString()}
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }