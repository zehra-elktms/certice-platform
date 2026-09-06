class ISORiskCalculator:
    @staticmethod
    def calculate_risk(severity: int, probability: int) -> dict:
        score = severity * probability
        if score >= 15:
            risk_level = "CRITICAL"
            acceptable = False
        elif score >= 10:
            risk_level = "HIGH"
            acceptable = False
        elif score >= 5:
            risk_level = "MEDIUM"
            acceptable = True
        else:
            risk_level = "LOW"
            acceptable = True
        return {
            "score": score,
            "risk_level": risk_level,
            "is_acceptable": acceptable
        }
