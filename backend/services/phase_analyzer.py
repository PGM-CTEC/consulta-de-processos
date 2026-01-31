class PhaseAnalyzer:
    @staticmethod
    def analyze(class_name: str, movements: list, tribunal: str = "", grau: str = "G1") -> str:
        """
        Determines the process phase based on class, movements, and court level (grau).
        """
        class_name = (class_name or "").lower()
        grau = (grau or "G1").upper()
        
        # 0. Archive Phase (Highest priority)
        if movements:
            try:
                # Sort to find the latest
                sorted_movs = sorted(movements, key=lambda x: x.get("dataHora", ""), reverse=True)
                last_mov = sorted_movs[0]
                last_name = (last_mov.get("nome") or "").lower()
                last_code = str(last_mov.get("codigo"))
                # Code 22: Baixa Definitiva, 246: Arquivamento
                if any(k in last_name for k in ["baixa", "arquiv"]) or last_code in ["22", "246"]:
                    return "Arquivado / Baixa Definitiva"
            except:
                pass

        # 1. Execution Phase
        if "execução" in class_name or "cumprimento" in class_name:
            return "Fase Executiva"
            
        # Check movements for execution keywords or code 11385
        if movements:
            for mov in movements:
                m_name = (mov.get("nome") or "").lower()
                m_code = str(mov.get("codigo"))
                if "execução" in m_name or "cumprimento de sentença" in m_name or m_code == "11385":
                    return "Fase Executiva"

        # 2. Res Judicata (Trânsito em Julgado)
        for mov in movements:
            name = (mov.get("nome") or "").lower()
            code = str(mov.get("codigo"))
            if "trânsito em julgado" in name or code == "848":
                return "Trânsito em Julgado"

        # 3. Determine Knowledge Phase Level
        if grau == "G1":
            # Check if it was sent to 2nd instance
            if movements:
                try:
                    sorted_movs = sorted(movements, key=lambda x: x.get("dataHora", ""), reverse=True)
                    # If recent movements indicate remittance to higher court
                    for mov in sorted_movs[:5]: # check last 5 for remessa
                        name = (mov.get("nome") or "").lower()
                        if "remessa" in name and "tribunal" in name:
                            return "Conhecimento 2ª Instância (Em Recurso)"
                except:
                    pass
            return "Conhecimento 1ª Instância"
            
        elif grau == "G2":
            return "Conhecimento 2ª Instância"
            
        elif grau in ["STJ", "STF", "SUP"]:
            return "Conhecimento Instâncias Superiores"

        return "Conhecimento"
