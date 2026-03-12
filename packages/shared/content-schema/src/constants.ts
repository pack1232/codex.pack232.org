/** Valid audience values for roles */
export const ROLE_AUDIENCES = ['adult', 'youth', 'both'] as const;

/** Valid task categories */
export const TASK_CATEGORIES = [
  'administrative',
  'financial',
  'fundraising',
  'outdoor',
  'program',
  'recognition',
  'recruitment',
  'service',
  'training',
] as const;

/** Valid event categories */
export const EVENT_CATEGORIES = [
  'ceremonies',
  'fundraising',
  'outdoor',
  'outings',
  'program',
  'recruitment',
  'service',
] as const;

/** Valid training types */
export const TRAINING_TYPES = [
  'courses',
  'learning-plans',
  'programs',
] as const;

/** Valid frequency values */
export const FREQUENCIES = [
  'annual',
  'monthly',
  'quarterly',
  'ad-hoc',
  'once',
  'weekly',
  'biweekly',
  'as-needed',
] as const;
