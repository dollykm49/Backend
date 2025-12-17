import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://dfmdnpsnkxwgxjjgxhid.supabase.co'
const supabaseKey = process.env.SUPABASE_KEY   // Only safe on backend

export const supabase = createClient(supabaseUrl, supabaseKey)
