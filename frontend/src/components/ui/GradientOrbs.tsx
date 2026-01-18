import { motion } from 'framer-motion';
import { orbFloatVariants, orbFloatVariants2 } from '../../styles/animations';

interface GradientOrbsProps {
  mode?: 'HOLD' | 'FOLLOW';
  className?: string;
}

export function GradientOrbs({ mode = 'HOLD', className = '' }: GradientOrbsProps) {
  const isHold = mode === 'HOLD';

  return (
    <div className={`fixed inset-0 overflow-hidden pointer-events-none ${className}`}>
      {/* Primary orb */}
      <motion.div
        className="absolute w-[600px] h-[600px] rounded-full blur-[120px]"
        style={{
          background: isHold
            ? 'radial-gradient(circle, rgba(14, 165, 233, 0.12) 0%, transparent 70%)'
            : 'radial-gradient(circle, rgba(249, 115, 22, 0.10) 0%, transparent 70%)',
          top: '-10%',
          right: '-10%',
        }}
        variants={orbFloatVariants}
        animate="animate"
      />

      {/* Secondary orb */}
      <motion.div
        className="absolute w-[500px] h-[500px] rounded-full blur-[100px]"
        style={{
          background: isHold
            ? 'radial-gradient(circle, rgba(20, 184, 166, 0.10) 0%, transparent 70%)'
            : 'radial-gradient(circle, rgba(251, 146, 60, 0.08) 0%, transparent 70%)',
          bottom: '-5%',
          left: '-5%',
        }}
        variants={orbFloatVariants2}
        animate="animate"
      />

      {/* Tertiary accent orb */}
      <motion.div
        className="absolute w-[300px] h-[300px] rounded-full blur-[80px]"
        style={{
          background: isHold
            ? 'radial-gradient(circle, rgba(59, 130, 246, 0.08) 0%, transparent 70%)'
            : 'radial-gradient(circle, rgba(244, 63, 94, 0.06) 0%, transparent 70%)',
          top: '40%',
          left: '30%',
        }}
        variants={orbFloatVariants}
        animate="animate"
        transition={{ delay: 5 }}
      />
    </div>
  );
}
