import { z } from 'zod';
import {
  ROLE_AUDIENCES,
  TASK_CATEGORIES,
  EVENT_CATEGORIES,
  TRAINING_TYPES,
  FREQUENCIES,
} from './constants.js';

// ── Slug pattern: lowercase, hyphens, digits ─────────────────────────────
const slugPattern = /^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$/;
const slug = z.string().regex(slugPattern, 'Must be a valid slug (lowercase, hyphens, digits)');

// ── Jekyll compatibility fields (optional, ignored by Astro) ─────────────
const jekyllFields = {
  parent: z.string().optional(),
  nav_order: z.number().optional(),
  nav_exclude: z.boolean().optional(),
  layout: z.string().optional(),
  permalink: z.string().optional(),
  has_children: z.boolean().optional(),
};

// ── Role Schema ──────────────────────────────────────────────────────────

export const roleSchema = z.object({
  title: z.string(),
  role_id: slug,
  audience: z.enum(ROLE_AUDIENCES),
  description: z.string().optional(),
  unit_type: z.enum(['pack', 'troop', 'crew', 'any']).optional(),
  works_with: z.array(slug).optional(),
  related_youth_roles: z.array(slug).optional(),
  related_adult_roles: z.array(slug).optional(),
  training_required: z.array(z.string()).optional(),
  ...jekyllFields,
});

export type Role = z.infer<typeof roleSchema>;

// ── Task Schema ──────────────────────────────────────────────────────────

export const taskSchema = z.object({
  title: z.string(),
  task_id: slug,
  category: z.enum(TASK_CATEGORIES),
  frequency: z.string(), // Broader than enum — some tasks have custom frequencies
  owner: slug,
  roles: z.array(slug),
  months: z.union([z.array(z.number()), z.number()]).nullable().optional(),
  timing_note: z.string().optional(),
  event: slug.optional(),
  tags: z.array(z.string()).optional(),
  ...jekyllFields,
});

export type Task = z.infer<typeof taskSchema>;

// ── Event Schema ─────────────────────────────────────────────────────────

export const eventSchema = z.object({
  title: z.string(),
  event_id: slug,
  category: z.enum(EVENT_CATEGORIES),
  frequency: z.string(),
  owner: slug,
  roles: z.array(slug),
  months: z.union([z.array(z.number()), z.number()]).nullable().optional(),
  timing_note: z.string().optional(),
  venue: z.string().optional(),
  ...jekyllFields,
});

export type Event = z.infer<typeof eventSchema>;

// ── Training Schema ──────────────────────────────────────────────────────

export const trainingSchema = z.object({
  title: z.string(),
  training_id: z.union([z.string(), z.number()]),
  training_code: z.union([z.string(), z.number()]).optional(),
  type: z.enum(TRAINING_TYPES),
  duration: z.union([z.string(), z.number()]).optional(),
  description: z.string().optional(),
  url: z.string().url().optional(),
  ...jekyllFields,
});

export type Training = z.infer<typeof trainingSchema>;

// ── Union type for any content item ──────────────────────────────────────

export const contentItemSchema = z.discriminatedUnion('_type', [
  roleSchema.extend({ _type: z.literal('role') }),
  taskSchema.extend({ _type: z.literal('task') }),
  eventSchema.extend({ _type: z.literal('event') }),
  trainingSchema.extend({ _type: z.literal('training') }),
]);

export type ContentItem = z.infer<typeof contentItemSchema>;
