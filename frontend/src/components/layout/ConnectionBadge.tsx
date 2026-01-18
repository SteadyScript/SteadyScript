import { motion } from 'framer-motion';
import { Wifi, WifiOff } from 'lucide-react';

interface ConnectionBadgeProps {
  isConnected: boolean;
  className?: string;
}

export function ConnectionBadge({ isConnected, className = '' }: ConnectionBadgeProps) {
  return (
    <motion.div
      className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${
        isConnected
          ? 'bg-teal-500/20 border border-teal-500/40'
          : 'bg-red-500/20 border border-red-500/40'
      } ${className}`}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
    >
      {/* Pulsing dot */}
      <div className="relative">
        <motion.div
          className={`w-2 h-2 rounded-full ${isConnected ? 'bg-teal-400' : 'bg-red-400'}`}
          animate={isConnected ? {
            scale: [1, 1.2, 1],
            opacity: [1, 0.8, 1],
          } : {}}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
        {isConnected && (
          <motion.div
            className="absolute inset-0 w-2 h-2 rounded-full bg-teal-400"
            animate={{
              scale: [1, 2],
              opacity: [0.6, 0],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeOut',
            }}
          />
        )}
      </div>

      {/* Icon */}
      {isConnected ? (
        <Wifi size={14} className="text-teal-400" />
      ) : (
        <WifiOff size={14} className="text-red-400" />
      )}

      {/* Text */}
      <span className={`text-xs font-medium ${isConnected ? 'text-teal-400' : 'text-red-400'}`}>
        {isConnected ? 'Connected' : 'Disconnected'}
      </span>
    </motion.div>
  );
}
