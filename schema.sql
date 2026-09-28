-- Ejecuta este script completo en Supabase: Dashboard > SQL Editor > New query

-- =========================================================
-- USUARIOS (registro / login propio + perfil deportivo, HU6)
-- =========================================================
create table if not exists users (
    id bigint generated always as identity primary key,
    name text not null,
    email text not null unique,
    password_hash text not null,
    sex text,                              -- "Masculino", "Femenino", "Otro"

    -- Perfil deportivo (Historia de Usuario 6)
    age integer,
    weight numeric,                        -- kg
    height numeric,                        -- cm
    experience_level text,                 -- "Principiante", "Intermedio", "Avanzado"
    goal text,                             -- "Perder peso", "Ganar masa muscular", "Salud general", "Competir"
    budget_monthly numeric,                -- presupuesto mensual disponible (Bs)
    available_days integer,                -- días disponibles por semana
    available_hours numeric,               -- horas libres por día para entrenar

    created_at timestamp with time zone default now()
);

-- =========================================================
-- DEPORTES
-- =========================================================
create table if not exists sports (
    id bigint generated always as identity primary key,
    name text not null,
    category text not null,                -- "Equipo", "Individual", "Acuático", "Combate"
    gender text default 'Mixto',
    description text,
    how_it_works text,
    average_cost text,
    cost_score smallint default 3,         -- 1 (barato) - 5 (caro)
    time_commitment text,
    time_score smallint default 3,         -- 1 (poco tiempo) - 5 (mucho tiempo)
    funding_score smallint default 3,      -- 1 (poco apoyo/remuneración) - 5 (mucho)
    difficulty_level text,                 -- "Principiante", "Intermedio", "Avanzado"
    equipment_required text,               -- Historia de Usuario 1 y 4: equipamiento necesario
    physical_benefits text,                -- Historia de Usuario 1: beneficios físicos
    recommendations text,
    diet_recommendations text,
    image_url text,
    created_at timestamp with time zone default now()
);

-- =========================================================
-- REGISTROS DE ENTRENAMIENTO (control de entrenamiento, HU5)
-- =========================================================
create table if not exists training_logs (
    id bigint generated always as identity primary key,
    user_id bigint references users(id) on delete cascade,
    sport_id bigint references sports(id) on delete cascade,
    weight numeric not null,
    height numeric not null,
    sex text,
    level text,
    daily_minutes integer,
    available_days integer,                -- días/semana usados para planificar
    custom_routine text,
    imc numeric,
    created_at timestamp with time zone default now()
);

-- =========================================================
-- CÁLCULOS DE COSTO GUARDADOS (Historia de Usuario 4)
-- =========================================================
create table if not exists cost_estimates (
    id bigint generated always as identity primary key,
    user_id bigint references users(id) on delete cascade,
    sport_id bigint references sports(id) on delete cascade,
    months integer not null,
    inscripcion numeric default 0,
    mensualidad numeric default 0,
    alquiler numeric default 0,
    equipamiento numeric default 0,
    vestimenta numeric default 0,
    transporte numeric default 0,
    alimentacion numeric default 0,
    monthly_total numeric,
    period_total numeric,
    created_at timestamp with time zone default now()
);

-- =========================================================
-- Nota sobre HU3 (calculadora de calorías): el registro de
-- alimentos del día se guarda en la sesión del usuario (Flask
-- session), no en una tabla, para mantener el MVP simple. Si el
-- equipo quiere persistirlo entre sesiones, se puede agregar una
-- tabla "food_log(user_id, nombre, kcal, fecha)" más adelante.
-- =========================================================

-- =========================================================
-- Seguridad básica (ajustar antes de producción real)
-- =========================================================
alter table users enable row level security;
alter table sports enable row level security;
alter table training_logs enable row level security;
alter table cost_estimates enable row level security;

create policy "sports lectura publica" on sports for select using (true);
create policy "sports insert" on sports for insert with check (true);
create policy "sports update" on sports for update using (true);
create policy "sports delete" on sports for delete using (true);

create policy "users insert (registro)" on users for insert with check (true);
create policy "users lectura" on users for select using (true);
create policy "users update (perfil)" on users for update using (true);

create policy "training_logs insert" on training_logs for insert with check (true);
create policy "training_logs lectura" on training_logs for select using (true);
create policy "training_logs delete" on training_logs for delete using (true);

create policy "cost_estimates insert" on cost_estimates for insert with check (true);
create policy "cost_estimates lectura" on cost_estimates for select using (true);
