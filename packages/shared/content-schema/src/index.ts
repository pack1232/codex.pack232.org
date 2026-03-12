/**
 * @justonehourperweek/content-schema
 *
 * Typed Zod schemas for the BSA content pack format.
 * Used by Astro content collections and the validation CLI.
 *
 * Content types:
 *   - Role:     A leadership position (adult, youth, or shared)
 *   - Task:     A recurring or one-time responsibility
 *   - Event:    A scheduled pack/troop event
 *   - Training: A BSA training course, learning plan, or program
 */

export {
  roleSchema,
  taskSchema,
  eventSchema,
  trainingSchema,
  contentItemSchema,
  type Role,
  type Task,
  type Event,
  type Training,
  type ContentItem,
} from './schemas.js';

export {
  ROLE_AUDIENCES,
  TASK_CATEGORIES,
  EVENT_CATEGORIES,
  TRAINING_TYPES,
  FREQUENCIES,
} from './constants.js';
