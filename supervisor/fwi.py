import math

class FWI:
    def safe_float(self, value, default=0.0):
        """Safely convert value to float, handle None, 'N/A', and invalid values"""
        if value is None or value == "N/A" or value == "":
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def FFMC(self, TEMP, RH, WIND, RAIN, FFMCPrev):
        TEMP = self.safe_float(TEMP, 20.0)
        RH = self.safe_float(RH, 50.0) 
        WIND = self.safe_float(WIND, 0.0)
        RAIN = self.safe_float(RAIN, 0.0)
        FFMCPrev = self.safe_float(FFMCPrev, 85.0)
        
        RH = min(100.0, RH)
        mo = 147.2 * (101.0 - FFMCPrev) / (59.5 + FFMCPrev)

        if RAIN > 0.5:
            rf = RAIN - 0.5
            if mo <= 150.0:
                mr = mo + 42.5 * rf * math.exp(-100.0 / (251.0 - mo)) * (1.0 - math.exp(-6.93 / rf))
            else:
                mr = mo + 42.5 * rf * math.exp(-100.0 / (251.0 - mo)) * (1.0 - math.exp(-6.93 / rf)) \
                     + 0.0015 * pow(mo - 150.0, 2) * pow(rf, 0.5)
            mr = min(mr, 250.0)
            mo = mr

        ed = 0.942 * pow(RH, 0.679) + 11.0 * math.exp((RH - 100.0) / 10.0) \
             + 0.18 * (21.1 - TEMP) * (1.0 - math.exp(-0.115 * RH))

        if mo > ed:
            ko = 0.424 * (1.0 - pow(RH / 100.0, 1.7)) + 0.0694 * pow(WIND, 0.5) * (1.0 - pow(RH / 100.0, 8))
            kd = ko * 0.581 * math.exp(0.0365 * TEMP)
            m = ed + (mo - ed) * pow(10.0, -kd)
        else:
            ew = 0.618 * pow(RH, 0.753) + 10.0 * math.exp((RH - 100.0) / 10.0) \
                 + 0.18 * (21.1 - TEMP) * (1.0 - math.exp(-0.115 * RH))
            if mo < ew:
                k1 = 0.424 * (1.0 - pow((100.0 - RH) / 100.0, 1.7)) \
                     + 0.0694 * pow(WIND, 0.5) * (1.0 - pow((100.0 - RH) / 100.0, 8))
                kw = k1 * 0.581 * math.exp(0.0365 * TEMP)
                m = ew - (ew - mo) * pow(10.0, -kw)
            else:
                m = mo

        return 59.5 * (250.0 - m) / (147.2 + m)

    def ISI(self, WIND, FFMC):
        WIND = self.safe_float(WIND, 0.0)
        FFMC = self.safe_float(FFMC, 85.0)
        
        fWIND = math.exp(0.05039 * WIND)
        m = 147.2 * (101.0 - FFMC) / (59.5 + FFMC)
        fF = 91.9 * math.exp(-0.1386 * m) * (1.0 + pow(m, 5.31) / 49300000.0)
        return 0.208 * fWIND * fF
       
    def FWI(self, ISI):
        ISI = self.safe_float(ISI, 0.0)
        return ISI * 0.1
        
    def calculate_wind(self, temp, humidity, pressure):
        """
        Estimate wind speed (m/s) from temperature (°C), humidity (%), and pressure (Pa or hPa).
        Automatically detects pressure unit and converts to hPa if necessary.
        """

        temp = self.safe_float(temp, 20.0)
        humidity = self.safe_float(humidity, 50.0)
        pressure = self.safe_float(pressure, 1013.25)

        # If pressure is in Pa (≥ 20000), convert to hPa
        if pressure > 2000:
            pressure = pressure / 100.0

        # Convert temperature to Kelvin
        temp_k = temp + 273.15

        # Saturation vapor pressure (Tetens formula)
        es = 6.112 * math.exp((17.67 * temp) / (temp + 243.5))

        # Actual vapor pressure
        ea = humidity / 100.0 * es

        # Air density (kg/m³) with humidity effect
        Rd = 287.05  # Gas constant for dry air
        Rv = 461.495 # Gas constant for water vapor
        rho = ((pressure * 100) - (ea * 100)) / (Rd * temp_k) + (ea * 100) / (Rv * temp_k)

        # Reference density at sea level
        ref_rho = 1.225
        density_diff = max(0, ref_rho - rho)

        # Convert density difference into estimated wind speed
        wind_speed = density_diff * 100
        return round(wind_speed, 2)

         
    def DMC(self, TEMP, RH, RAIN, dmc_prev):
        TEMP = self.safe_float(TEMP, 20.0)
        RH = self.safe_float(RH, 50.0)
        RAIN = self.safe_float(RAIN, 0.0)
        dmc_prev = self.safe_float(dmc_prev, 6.0)
        
        if RAIN > 1.5:
            Pr = RAIN
        else:
            Pr = 0.0

        if Pr > 0.0:
            Re = 0.92 * Pr - 1.27
            Mr = dmc_prev + 100.0 * Re
            if Mr < 0.0:
                Mr = 0.0
        else:
            Mr = dmc_prev

        rk = 1.894 * (TEMP + 1.1) * (100.0 - RH) * 0.0001
        dmc = Mr + rk

        # Limit value between 0 and 300
        dmc = max(0, min(dmc, 300))
        return round(dmc, 2)


"""import math

class FWI:
    def safe_float(self, value, default=0.0):
        #Safely convert value to float, handle None, 'N/A', and invalid values
        if value is None or value == "N/A" or value == "":
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def FFMC(self, TEMP, RH, WIND, RAIN, FFMCPrev):
        # Convert inputs to safe float values
        TEMP = self.safe_float(TEMP, 20.0)
        RH = self.safe_float(RH, 50.0) 
        WIND = self.safe_float(WIND, 0.0)
        RAIN = self.safe_float(RAIN, 0.0)
        FFMCPrev = self.safe_float(FFMCPrev, 85.0)
        
        RH = min(100.0, RH)
        mo = 147.2 * (101.0 - FFMCPrev) / (59.5 + FFMCPrev)

        if RAIN > .5:
            rf = RAIN - .5
            if mo <= 150.0:
                mr = mo + 42.5 * rf * math.exp(-100.0 / (251.0 - mo)) * (1.0 - math.exp(-6.93 / rf))
            else:
                mr = mo + 42.5 * rf * math.exp(-100.0 / (251.0 - mo)) * (1.0 - math.exp(-6.93 / rf)) + 0.0015 * pow(mo - 150.0, 2) * pow(rf, .5)
            if mr > 250.0:
                mr = 250.0
            mo = mr

        ed = 0.942 * pow(RH, 0.679) + 11.0 * math.exp((RH - 100.0) / 10.0) + 0.18 * (21.1 - TEMP) * (1.0 - math.exp(-0.115 * RH))

        if mo > ed:
            ko = 0.424 * (1.0 - pow(RH / 100.0, 1.7)) + 0.0694 * pow(WIND, .5) * (1.0 - pow(RH / 100.0, 8))
            kd = ko * 0.581 * math.exp(0.0365 * TEMP)
            m = ed + (mo - ed) * pow(10.0, -kd)
        else:
            ew = 0.618 * pow(RH, 0.753) + 10.0 * math.exp((RH - 100.0) / 10.0) + 0.18 * (21.1 - TEMP) * (1.0 - math.exp(-0.115 * RH))
            if mo < ew:
                k1 = 0.424 * (1.0 - pow((100.0 - RH) / 100.0, 1.7)) + 0.0694 * pow(WIND, .5) * (1.0 - pow((100.0 - RH) / 100.0, 8))
                kw = k1 * 0.581 * math.exp(0.0365 * TEMP)
                m = ew - (ew - mo) * pow(10.0, -kw)
            else:
                m = mo

        return 59.5 * (250.0 - m) / (147.2 + m)

    def ISI(self, WIND, FFMC):
        # Convert inputs to safe float values
        WIND = self.safe_float(WIND, 0.0)
        FFMC = self.safe_float(FFMC, 85.0)
        
        fWIND = math.exp(0.05039 * WIND)
        m = 147.2 * (101.0 - FFMC) / (59.5 + FFMC)
        fF = 91.9 * math.exp(-0.1386 * m) * (1.0 + pow(m, 5.31) / 49300000.0)
        return 0.208 * fWIND * fF
       
    def FWI(self, ISI):
        # Convert input to safe float value
        ISI = self.safe_float(ISI, 0.0)
        return ISI * 0.1
        
    def calculate_wind(self, temp, humidity, pressure):
        # Convert inputs to safe float values with appropriate defaults
        temp = self.safe_float(temp, 20.0)
        humidity = self.safe_float(humidity, 50.0)
        pressure = self.safe_float(pressure, 1013.25)
        
        wind_temp_factor = 0.1
        wind_humidity_factor = 0.07
        wind_pressure_factor = 0.05

        wind_from_temp = temp * wind_temp_factor
        wind_from_humidity = humidity * wind_humidity_factor
        wind_from_pressure = (1013 - pressure) * wind_pressure_factor

        estimated_wind_speed = wind_from_temp + wind_from_humidity + wind_from_pressure
        return round(max(0, estimated_wind_speed), 2)
         
    def DMC(self, TEMP, RH, RAIN, dmc_prev):
        # Convert inputs to safe float values
        TEMP = self.safe_float(TEMP, 20.0)
        RH = self.safe_float(RH, 50.0)
        RAIN = self.safe_float(RAIN, 0.0)
        dmc_prev = self.safe_float(dmc_prev, 6.0)
        
        if RAIN > 1.5:
            Pr = RAIN
        else:
            Pr = 0.0

        if Pr > 0.0:
            Re = 0.92 * Pr - 1.27
            Mr = dmc_prev + 100.0 * Re
            if Mr < 0.0:
              Mr = 0.0
        else:
             Mr = dmc_prev

        rk = 1.894 * (TEMP + 1.1) * (100.0 - RH) * 0.0001
        dmc = Mr + rk

        # Limiter la valeur entre 0 et 300 comme recommandé
        dmc = max(0, min(dmc, 300))
        return round(dmc, 2)"""