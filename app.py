import streamlit as st
import math

class Planet:
    # Constants
    G = 6.67430e-11
    M_earth = 5.972e24
    R_earth = 6.371e6
    AU_in_meters = 1.496e11  # 1 Astronomical Unit in meters

    def __init__(self, mass=1.0, radius=1.0, distance_from_star=1.0,
                 star_type=1, albedo=0.3, atmosphere_type=0):
        # Mass of the planet relative to Earth (Earth = 1.0)
        self.mass = mass

        # Radius of the planet relative to Earth (Earth = 1.0)
        self.radius = radius

        # Distance from the star in Astronomical Units (AU)
        self.distance_from_star = distance_from_star

        # Star type index: 0 = Red Dwarf, 1 = G-type (Sun), 2 = A-type (Sirius)
        self.star_type = star_type

        # Albedo: How reflective the surface is (Earth average = 0.3)
        self.albedo = albedo

        #The type of the atmosphere
        self.atmosphere_type = atmosphere_type

        # Physical conversions to SI units
        self.actual_mass = self.mass * self.M_earth
        self.actual_radius = self.radius * self.R_earth
        self.actual_distance = self.distance_from_star * self.AU_in_meters

        # Assign star properties based on selection (Temperature in K, Radius in meters)
        if self.star_type == 0:  # Proxima Centauri (M-type)
            self.star_temperature = 3042
            self.star_radius = 1.07e8
        elif self.star_type == 1:  # Sun (G-type)
            self.star_temperature = 5778
            self.star_radius = 6.957e8
        elif self.star_type == 2:  # Sirius A (A-type)
            self.star_temperature = 9940
            self.star_radius = 1.19e9

    def surface_gravity(self):
        # Returns surface gravity relative to Earth (g_rel)
        return self.mass / (self.radius**2)

    def escape_velocity(self):
        # Calculates escape velocity in meters per second (m/s)
        # Formula: sqrt(2GM / R)
        v = math.sqrt((2 * self.G * self.actual_mass) / self.actual_radius)
        return v

    def surface_temperature(self):
        # Calculates Equilibrium Temperature (T_eq) in Kelvins
        # Assumes the planet acts as a blackbody without greenhouse effect
        # Formula: T_star * sqrt(R_star / 2D) * (1-a)^(1/4)
        t_eq = (self.star_temperature * math.sqrt(self.star_radius / (2 * self.actual_distance)) * (1 - self.albedo)**(1/4))
        return t_eq

    
    def final_temperature(self):
        t_eq = self.surface_temperature() # Kaava C tulos
    
        # Lisätään kasvihuoneilmiö (Greenhouse Effect)
        # Maa = n. 33K lisäys
        if self.atmosphere_type == 2:
            return t_eq + 33
        elif self.atmosphere_type == 1:
            return t_eq + 5
        elif self.atmosphere_type == 3:
            return t_eq + 150
        elif self.atmosphere_type == 0:
            return t_eq
        return t_eq
    

    def jump_height(self):
        # Estimate: A human jumps approx. 0.5m on Earth.
        # Jump height is inversely proportional to gravity.
        g_rel = self.surface_gravity()
        return 0.5 / g_rel # Result in meters

    def average_height(self):
        # Biological estimate: Inhabitants are likely shorter in high gravity.
        # Uses the Square-Cube Law logic: height scales with 1/sqrt(g).
        g_rel = self.surface_gravity()
        base_human_height = 1.75 # meters
        return base_human_height / math.sqrt(g_rel)

    def bone_density(self):
        # Bone density must increase relative to gravity to support body weight.
        # Returns factor relative to Earth humans (Earth = 1.0)
        return self.surface_gravity()



# --- STREAMLIT UI ---
st.set_page_config(page_title="Hard Sci-Fi Planet Engine", layout="centered")

st.title("Project Exo: Planet Simulator")
st.markdown("Build scientifically accurate worlds.")

# --- SIDEBAR INPUTS ---
st.header("Planetary Parameters")
col1, col2 = st.columns(2)

mass = col1.slider("Mass (Earths)", 0.1, 10.0, 1.0)
radius = col1.slider("Radius (Earths)", 0.5, 5.0, 1.0)
distance = col2.slider("Distance from Star (AU)", 0.01, 10.0, 1.0)
albedo = col1.slider("Albedo", 0.0, 1.0, 1.0)

# Määritellään kuvaus albedon arvon perusteella
if albedo <= 0.1:
    surface_desc = "🌑 **Absorbent:** Very dark surface, like charcoal or asphalt. Absorbs almost all light."
elif albedo <= 0.2:
    surface_desc = "🌑 **Dark:** Moon-like surface (basaltic rock). Deep forests or dark soil."
elif albedo <= 0.4:
    surface_desc = "🌍 **Earth-like:** Moderate reflection. A mix of oceans, vegetation, and average cloud cover."
elif albedo <= 0.6:
    surface_desc = "🏜️ **Bright:** Highly reflective. Vast deserts, light-colored rocks, or significant cloud cover."
elif albedo <= 0.8:
    surface_desc = "❄️ **Icy / Cloudy:** Very bright. Thick clouds or large ice sheets/glaciers."
else:
    surface_desc = "💎 **Highly Reflective:** Fresh snow or a planet-wide cloud layer. Mirror-like brightness."

# Näytetään kuvaus suoraan säätimen alapuolella
col1.markdown(surface_desc)

star_choice = col2.selectbox("Star Type",
                                  options=[0, 1, 2],
                                  format_func=lambda x: ["Red Dwarf", "Sun-like", "Sirius-like"][x])

atmosphere_choice = col2.selectbox("Atmosphere Type",
                                 options=[0, 1, 2, 3],
                                 format_func=lambda x: ["None", "Thin", "Earth-like", "Thic"][x])
# --- LOGIC ---
p = Planet(mass=mass, radius=radius, distance_from_star=distance, star_type=star_choice, albedo=albedo, atmosphere_type=atmosphere_choice)

# --- OUTPUTS ---
st.header("Results")

# Metrics in a row
col1, col2, col3 = st.columns(3)
col1.metric("Surface Gravity", f"{p.surface_gravity():.2f} g")
col2.metric("Temp (Est.)", f"{p.final_temperature() - 273.15:.1f} °C")
col3.metric("Escape Velocity", f"{p.escape_velocity()/1000:.2f} km/s")

# Scientific analysis
st.subheader("Scientific Analysis")

esc_vel_km_s = p.escape_velocity() / 1000
gravity = p.surface_gravity()

# Ehto 1: Ilmakehän säilyminen (karkea fysiikka-arvio)
if esc_vel_km_s < 3.0:
    st.error("🚨 **Atmospheric Loss:** Escape velocity is too low. This planet cannot retain a significant atmosphere (like Mars or Moon).")
elif esc_vel_km_s < 6.0:
    st.warning("⚠️ **Thin Atmosphere:** Low escape velocity suggests a thin atmosphere, likely lacking heavy gases like Oxygen.")
else:
    st.success("✅ **Atmosphere Retention:** Escape velocity is sufficient to retain a thick, Earth-like atmosphere.")

# Ehto 2: Biologinen rasitus
if gravity > 2.0:
    st.info("🦾 **Exoskeleton Required:** Gravity is over 2g. Human biology would fail without mechanical support or extreme genetic engineering.")


st.divider()

# Biological insights
st.subheader("Biological Implications")
st.write(f"🏃 **Jump Height:** You could jump about **{p.jump_height():.2f} meters** high.")
st.write(f"📏 **Average Inhabitant:** A typical humanoid would be roughly **{p.average_height():.2f} m** tall.")

st.write(f"🦴 **Bone Density:** Skeletal structures must be **{p.bone_density():.1f}x** stronger than human bones.")








