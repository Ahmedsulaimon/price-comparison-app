from rapidfuzz import fuzz


class ProductGrouper:
    def group_products(self, products: list) -> list:
        """Group similar products across retailers"""
        groups = []
        seen = set()
        
        for product in products:
            if product['id'] in seen:
                continue
                
            # Find similar products
            similar = self._find_similar(product, products)
            groups.append(similar)
            seen.update(p['id'] for p in similar)
            
        return groups

    def _find_similar(self, target: dict, products: list) -> list:
        """Find similar products using weight thresholds"""
        target_specs = self._extract_specs(target['name'])
        similar = []
        
        for p in products:
            if p['id'] == target['id']:
                similar.append(p)
                continue
                
            p_specs = self._extract_specs(p['name'])
            match_score = self._calc_match_score(target_specs, p_specs)
            
            if match_score >= 0.7:  # Adjust threshold as needed
                similar.append(p)
                
        return similar

    def _extract_specs(self, name: str) -> dict:
        """Extract product specifications from name"""
        return {
            'weight': self._extract_weight(name),
            'count': self._extract_count(name),
            'variety': self._extract_variety(name)
        }

    def _calc_match_score(self, target: dict, candidate: dict) -> float:
        """Calculate similarity score between products"""
        weight_score = 1 if target['weight'] == candidate['weight'] else 0
        count_score = 1 if target['count'] == candidate['count'] else 0
        variety_score = fuzz.ratio(target['variety'], candidate['variety'])/100
        
        return 0.4*weight_score + 0.4*count_score + 0.2*variety_score