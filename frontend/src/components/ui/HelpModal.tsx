import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, Info } from 'lucide-react';

interface HelpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

// Simple hand grip SVG illustrations
function DynamicTripodGrip() {
  return (
    <svg viewBox="0 0 120 120" className="w-full h-full">
      {/* Pencil */}
      <rect x="50" y="10" width="8" height="80" rx="2" fill="#f59e0b" />
      <polygon points="54,90 50,100 58,100" fill="#fbbf24" />
      <rect x="50" y="10" width="8" height="8" rx="1" fill="#ec4899" />

      {/* Hand outline - thumb */}
      <path
        d="M40 55 Q35 50 38 42 Q42 35 48 40 L50 50"
        fill="none"
        stroke="#94a3b8"
        strokeWidth="2.5"
        strokeLinecap="round"
      />

      {/* Index finger */}
      <path
        d="M58 50 Q62 45 65 38 Q67 32 70 35 Q73 40 68 50 Q65 55 60 58"
        fill="none"
        stroke="#94a3b8"
        strokeWidth="2.5"
        strokeLinecap="round"
      />

      {/* Middle finger */}
      <path
        d="M58 58 Q65 60 72 55 Q78 52 80 58 Q78 65 70 68 L60 65"
        fill="none"
        stroke="#94a3b8"
        strokeWidth="2.5"
        strokeLinecap="round"
      />

      {/* Ring and pinky (curled) */}
      <path
        d="M60 70 Q70 75 75 80 Q78 88 70 92 Q62 90 58 82"
        fill="none"
        stroke="#94a3b8"
        strokeWidth="2"
        strokeLinecap="round"
        strokeDasharray="3,2"
      />

      {/* Contact points */}
      <circle cx="50" cy="48" r="3" fill="#10b981" />
      <circle cx="58" cy="52" r="3" fill="#10b981" />
      <circle cx="58" cy="62" r="3" fill="#10b981" />
    </svg>
  );
}

function LateralTripodGrip() {
  return (
    <svg viewBox="0 0 120 120" className="w-full h-full">
      {/* Pencil - more angled */}
      <rect x="45" y="15" width="8" height="75" rx="2" fill="#f59e0b" transform="rotate(-15 49 52)" />
      <polygon points="40,88 35,98 43,98" fill="#fbbf24" />
      <rect x="58" y="8" width="8" height="8" rx="1" fill="#ec4899" transform="rotate(-15 62 12)" />

      {/* Thumb - across the pencil */}
      <path
        d="M35 50 Q30 45 32 38 Q38 32 45 38 L48 48"
        fill="none"
        stroke="#94a3b8"
        strokeWidth="2.5"
        strokeLinecap="round"
      />

      {/* Index finger - wrapped */}
      <path
        d="M52 45 Q58 40 62 35 Q66 30 70 35 Q72 42 65 50 L55 55"
        fill="none"
        stroke="#94a3b8"
        strokeWidth="2.5"
        strokeLinecap="round"
      />

      {/* Middle finger - side support */}
      <path
        d="M48 58 Q55 62 62 58 Q70 55 72 62 Q70 70 60 72 L50 68"
        fill="none"
        stroke="#94a3b8"
        strokeWidth="2.5"
        strokeLinecap="round"
      />

      {/* Ring and pinky */}
      <path
        d="M52 72 Q60 78 65 85 Q66 92 58 94 Q50 90 48 82"
        fill="none"
        stroke="#94a3b8"
        strokeWidth="2"
        strokeLinecap="round"
        strokeDasharray="3,2"
      />

      {/* Contact points */}
      <circle cx="45" cy="46" r="3" fill="#10b981" />
      <circle cx="55" cy="48" r="3" fill="#10b981" />
      <circle cx="50" cy="60" r="3" fill="#10b981" />
    </svg>
  );
}

function QuadrupodGrip() {
  return (
    <svg viewBox="0 0 120 120" className="w-full h-full">
      {/* Pencil */}
      <rect x="50" y="10" width="8" height="80" rx="2" fill="#f59e0b" />
      <polygon points="54,90 50,100 58,100" fill="#fbbf24" />
      <rect x="50" y="10" width="8" height="8" rx="1" fill="#ec4899" />

      {/* Thumb */}
      <path
        d="M40 52 Q35 48 37 40 Q42 34 48 40 L50 48"
        fill="none"
        stroke="#94a3b8"
        strokeWidth="2.5"
        strokeLinecap="round"
      />

      {/* Index finger */}
      <path
        d="M58 48 Q62 42 66 36 Q70 32 74 36 Q76 44 70 52 L62 56"
        fill="none"
        stroke="#94a3b8"
        strokeWidth="2.5"
        strokeLinecap="round"
      />

      {/* Middle finger */}
      <path
        d="M58 56 Q64 56 70 52 Q76 50 78 56 Q76 64 68 66 L60 64"
        fill="none"
        stroke="#94a3b8"
        strokeWidth="2.5"
        strokeLinecap="round"
      />

      {/* Ring finger - also on pencil */}
      <path
        d="M58 66 Q64 68 68 65 Q74 64 76 70 Q74 78 66 78 L58 74"
        fill="none"
        stroke="#94a3b8"
        strokeWidth="2.5"
        strokeLinecap="round"
      />

      {/* Pinky */}
      <path
        d="M58 76 Q64 82 66 88 Q65 94 58 94 Q52 90 52 84"
        fill="none"
        stroke="#94a3b8"
        strokeWidth="2"
        strokeLinecap="round"
        strokeDasharray="3,2"
      />

      {/* Contact points - 4 fingers */}
      <circle cx="50" cy="46" r="3" fill="#10b981" />
      <circle cx="58" cy="50" r="3" fill="#10b981" />
      <circle cx="58" cy="60" r="3" fill="#10b981" />
      <circle cx="58" cy="70" r="3" fill="#10b981" />
    </svg>
  );
}

function AdaptedGrip() {
  return (
    <svg viewBox="0 0 120 120" className="w-full h-full">
      {/* Pencil with grip aid */}
      <rect x="50" y="10" width="8" height="80" rx="2" fill="#f59e0b" />
      <polygon points="54,90 50,100 58,100" fill="#fbbf24" />
      <rect x="50" y="10" width="8" height="8" rx="1" fill="#ec4899" />

      {/* Grip aid (foam/rubber triangle) */}
      <path
        d="M46 40 L54 35 L62 40 L58 55 L50 55 Z"
        fill="#3b82f6"
        fillOpacity="0.3"
        stroke="#3b82f6"
        strokeWidth="1.5"
      />

      {/* Thumb */}
      <path
        d="M38 52 Q33 48 35 40 Q40 34 46 40"
        fill="none"
        stroke="#94a3b8"
        strokeWidth="2.5"
        strokeLinecap="round"
      />

      {/* Index finger */}
      <path
        d="M62 40 Q68 38 72 34 Q76 32 78 38 Q78 46 72 52 L64 54"
        fill="none"
        stroke="#94a3b8"
        strokeWidth="2.5"
        strokeLinecap="round"
      />

      {/* Middle finger */}
      <path
        d="M58 58 Q66 60 72 58 Q78 56 80 62 Q78 70 70 72 L60 68"
        fill="none"
        stroke="#94a3b8"
        strokeWidth="2.5"
        strokeLinecap="round"
      />

      {/* Ring and pinky */}
      <path
        d="M60 72 Q68 78 72 86 Q70 94 62 94 Q54 90 54 82"
        fill="none"
        stroke="#94a3b8"
        strokeWidth="2"
        strokeLinecap="round"
        strokeDasharray="3,2"
      />

      {/* Contact points on grip aid */}
      <circle cx="48" cy="44" r="3" fill="#10b981" />
      <circle cx="60" cy="44" r="3" fill="#10b981" />
      <circle cx="54" cy="52" r="3" fill="#10b981" />
    </svg>
  );
}

const gripTypes = [
  {
    name: 'Dynamic Tripod',
    description: 'Thumb, index, and middle finger hold the pencil. Most common and recommended grip.',
    recommended: true,
    component: DynamicTripodGrip,
  },
  {
    name: 'Lateral Tripod',
    description: 'Thumb crosses over the pencil with index and middle finger support.',
    recommended: false,
    component: LateralTripodGrip,
  },
  {
    name: 'Quadrupod',
    description: 'Four fingers (thumb, index, middle, ring) stabilize the pencil.',
    recommended: false,
    component: QuadrupodGrip,
  },
  {
    name: 'Adapted Grip',
    description: 'Using a grip aid for better control. Great for reducing tremor.',
    recommended: true,
    component: AdaptedGrip,
  },
];

export function HelpModal({ isOpen, onClose }: HelpModalProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="w-full max-w-2xl rounded-2xl border overflow-hidden"
              style={{
                background: 'linear-gradient(145deg, #1e2128 0%, #191c22 100%)',
                borderColor: '#2a2f38',
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
              }}
              initial={{ scale: 0.95, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.95, y: 20 }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700/50">
                <h2 className="text-lg font-semibold text-white">Hand Grip Guide</h2>
                <button
                  onClick={onClose}
                  className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-700/50 transition-colors"
                >
                  <X size={20} />
                </button>
              </div>

              {/* Content */}
              <div className="p-6 max-h-[70vh] overflow-y-auto">
                {/* Intro */}
                <div className="flex items-start gap-3 p-4 rounded-xl bg-cyan-500/10 border border-cyan-500/20 mb-6">
                  <Info size={20} className="text-cyan-400 flex-shrink-0 mt-0.5" />
                  <div className="text-sm text-gray-300">
                    <p className="font-medium text-cyan-400 mb-1">How to hold your marker</p>
                    <p>
                      Choose a grip that feels comfortable and allows you to keep your hand steady.
                      The grip you use can affect your tremor measurements.
                    </p>
                  </div>
                </div>

                {/* Grip types grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {gripTypes.map((grip) => (
                    <motion.div
                      key={grip.name}
                      className="relative rounded-xl border p-4 transition-all hover:border-opacity-60"
                      style={{
                        background: 'linear-gradient(145deg, rgba(30, 33, 40, 0.6) 0%, rgba(25, 28, 34, 0.8) 100%)',
                        borderColor: grip.recommended ? 'rgba(16, 185, 129, 0.3)' : '#2a2f3830',
                      }}
                      whileHover={{ y: -2 }}
                    >
                      {/* Recommended badge */}
                      {grip.recommended && (
                        <div className="absolute top-3 right-3 flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 text-[10px] font-medium">
                          <CheckCircle size={10} />
                          Recommended
                        </div>
                      )}

                      {/* Illustration */}
                      <div className="w-24 h-24 mx-auto mb-3">
                        <grip.component />
                      </div>

                      {/* Name */}
                      <h3 className="text-sm font-semibold text-white text-center mb-1">
                        {grip.name}
                      </h3>

                      {/* Description */}
                      <p className="text-xs text-gray-400 text-center leading-relaxed">
                        {grip.description}
                      </p>
                    </motion.div>
                  ))}
                </div>

                {/* Tips */}
                <div className="mt-6 p-4 rounded-xl bg-gray-800/50">
                  <h3 className="text-sm font-medium text-white mb-2">Tips for better stability</h3>
                  <ul className="space-y-2 text-xs text-gray-400">
                    <li className="flex items-start gap-2">
                      <span className="text-cyan-400">1.</span>
                      Rest your wrist or forearm on a stable surface
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-cyan-400">2.</span>
                      Hold the marker lightly - don't grip too tightly
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-cyan-400">3.</span>
                      Take slow, deep breaths before starting
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-cyan-400">4.</span>
                      Consider using a grip aid for better control
                    </li>
                  </ul>
                </div>
              </div>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
