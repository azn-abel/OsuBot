import math


def computeTotalValue(score, beatmap, attributes):

    def getComboScalingFactor():
        maxCombo = beatmap['max_combo']
        if maxCombo > 0:
            return min((score['max_combo'] ** 0.8) / (maxCombo ** 0.8), 1.0)
        return 1.0

    def TotalHits():
        return score_statistics['count_300'] + score_statistics['count_100'] + score_statistics['count_50'] + score_statistics['count_miss']

    def Accuracy():
        if TotalHits() == 0:
            return 0.0

        # Factor in misses as 150, the mean of 50, 100, and 300
        acc = float(score_statistics['count_50'] * 50 + score_statistics['count_100'] * 100 + score_statistics['count_300'] * 300 + score_statistics['count_miss'] * 150) / (
                    TotalHits() * 300)

        if acc > 1.0:
            return 1.0
        elif acc < 0.0:
            return 0.0
        else:
            return acc

    def computeAimValue():
        aimValue = (5.0 * max(1.0, attributes['aim_difficulty'] / 0.0675) - 4.0) ** 3.0 / 100000.0

        lengthBonus = 0.95 + 0.4 * min(1.0, float(numTotalHits) / 2000.0) + (
            math.log10(float(numTotalHits) / 2000.0) * 0.5 if numTotalHits > 2000 else 0.0)
        aimValue *= lengthBonus

        # Penalize misses by assessing # of misses relative to the total # of objects. Default a 3% reduction for any # of misses.
        # if self.effectiveMissCount > 0:
        #     self.aimValue *= 0.97 * (1.0 - (self.effectiveMissCount / float(numTotalHits)) ** 0.775) ** self.effectiveMissCount

        aimValue *= getComboScalingFactor()

        approachRate = attributes['approach_rate']
        approachRateFactor = 0.0
        if approachRate > 10.33:
            approachRateFactor = 0.3 * (approachRate - 10.33)
        elif approachRate < 8.0:
            approachRateFactor = 0.05 * (8.0 - approachRate)

        aimValue *= 1.0 + approachRateFactor * lengthBonus

        # We want to give more reward for lower AR when it comes to aim and HD. This nerfs high AR and buffs lower AR.
        if "HD" in score['mods']:
            aimValue *= 1.0 + 0.04 * (12.0 - approachRate)

        # We assume 15% of sliders in a map are difficult since there's no way to tell from the performance calculator.
        estimateDifficultSliders = beatmap['count_sliders'] * 0.15

        if beatmap['count_sliders'] > 0:
            maxCombo = attributes['max_combo']
            estimateSliderEndsDropped = min(max(min(
                float(score_statistics['count_100'] + score_statistics['count_50'] + score_statistics['count_miss']),
                maxCombo - score['max_combo']), 0.0), estimateDifficultSliders)
            sliderFactor = attributes['slider_factor']
            sliderNerfFactor = (1.0 - sliderFactor) * (
                        1.0 - estimateSliderEndsDropped / estimateDifficultSliders) ** 3 + sliderFactor
            aimValue *= sliderNerfFactor

        aimValue *= Accuracy()
        # It is important to consider accuracy difficulty when scaling with accuracy.
        aimValue *= 0.98 + (attributes['overall_difficulty'] ** 2) / 2500
        return aimValue

    def computeSpeedValue():
        speedValue = (5.0 * max(1.0, attributes['speed_difficulty'] / 0.0675) - 4.0) ** 3.0 / 100000.0

        lengthBonus = 0.95 + 0.4 * min(1.0, float(numTotalHits) / 2000.0) + (
            math.log10(float(numTotalHits) / 2000.0) * 0.5 if numTotalHits > 2000 else 0.0)
        speedValue *= lengthBonus

        # Penalize misses by assessing # of misses relative to the total # of objects. Default a 3% reduction for any # of misses.
        # if self.effectiveMissCount > 0:
        #     self.speedValue *= 0.97 * (1.0 - (self.effectiveMissCount / float(numTotalHits)) ** 0.775) ** (self.effectiveMissCount ** 0.875)

        speedValue *= getComboScalingFactor()

        approachRate = attributes['approach_rate']
        approachRateFactor = 0.0
        if approachRate > 10.33:
            approachRateFactor = 0.3 * (approachRate - 10.33)

        speedValue *= 1.0 + approachRateFactor * lengthBonus  # Buff for longer maps with high AR.

        # We want to give more reward for lower AR when it comes to speed and HD. This nerfs high AR and buffs lower AR.
        if "HD" in score['mods']:
            speedValue *= 1.0 + 0.04 * (12.0 - approachRate)

        # Calculate accuracy assuming the worst case scenario
        relevantTotalDiff = float(numTotalHits) - attributes['speed_note_count']
        relevantCountGreat = max(0.0, score_statistics['count_300'] - relevantTotalDiff)
        relevantCountOk = max(0.0, score_statistics['count_100'] - max(0.0, relevantTotalDiff - score_statistics['count_300']))
        relevantCountMeh = max(0.0, score_statistics['count_50'] - max(0.0, relevantTotalDiff - score_statistics['count_300'] - score_statistics['count_100']))
        relevantAccuracy = (relevantCountGreat * 6.0 + relevantCountOk * 2.0 + relevantCountMeh) / (
                    attributes['speed_note_count'] * 6.0) if attributes['speed_note_count'] != 0.0 else 0.0

        # Scale the speed value with accuracy and OD.
        speedValue *= (0.95 + (attributes['overall_difficulty'] ** 2) / 750) * (
                    (Accuracy() + relevantAccuracy) / 2.0) ** (
                                  (14.5 - max(attributes['overall_difficulty'], 8.0)) / 2)

        # Scale the speed value with # of 50s to punish doubletapping.
        speedValue *= 0.99 ** (0.0 if score_statistics['count_50'] < numTotalHits / 500.0 else score_statistics['count_50'] - numTotalHits / 500.0)
        return speedValue

    def computeAccuracyValue():

        if "SV2" in mods:
            numHitObjectsWithAccuracy = TotalHits()
            betterAccuracyPercentage = Accuracy()
        else:
            numHitObjectsWithAccuracy = beatmap['count_circles']
            if numHitObjectsWithAccuracy > 0:
                betterAccuracyPercentage = float(
                    (score_statistics['count_300'] - (TotalHits() - numHitObjectsWithAccuracy)) * 6 + score_statistics['count_100'] * 2 + score_statistics[
                        'count_50']) / (numHitObjectsWithAccuracy * 6)
            else:
                betterAccuracyPercentage = 0.0

            if betterAccuracyPercentage < 0:
                betterAccuracyPercentage = 0.0

        accuracyValue = pow(1.52163, attributes['overall_difficulty']) * pow(betterAccuracyPercentage, 24) * 2.83

        accuracyValue *= min(1.15, pow(numHitObjectsWithAccuracy / 1000.0, 0.3))

        if "HD" in mods:
            accuracyValue *= 1.08

        if "FL" in mods:
            accuracyValue *= 1.02

        return accuracyValue

    def computeFlashlightValue():

        if "FL" not in mods:
            return 0

        flashlightValue = pow(attributes['flashlight_difficulty'], 2.0) * 25.0

        # if _effectiveMissCount > 0:
        #     _flashlightValue *= 0.97 * pow(1 - pow(_effectiveMissCount / float(numTotalHits), 0.775), pow(_effectiveMissCount, 0.875))

        flashlightValue *= getComboScalingFactor()

        flashlightValue *= 0.7 + 0.1 * min(1.0, float(numTotalHits) / 200.0) + (
            0.2 * min(1.0, (float(numTotalHits) - 200) / 200.0) if numTotalHits > 200 else 0.0)

        flashlightValue *= 0.5 + Accuracy() / 2.0
        flashlightValue *= 0.98 + pow(attributes['overall_difficulty'], 2.0) / 2500.0
        print(flashlightValue)
        return flashlightValue

    mods = score['mods']

    # Don't count scores made with supposedly unranked mods
    if "RL" in mods or "AP" in mods or "AT" in mods:
        return 0

    multiplier = 1.14  # This is being adjusted to keep the final pp value scaled around what it used to be when changing things.

    score_statistics = score['statistics']

    numTotalHits = (score_statistics['count_300']
                    + score_statistics['count_100']
                    + score_statistics['count_50']
                    + score_statistics['count_miss'])
    if "SO" in mods:
        multiplier *= 1.0 - (beatmap['count_spinners'] / numTotalHits) ** 0.85

    totalValue = (
        (
            (computeAimValue() ** 1.1)
            + (computeSpeedValue() ** 1.1)
            + (computeAccuracyValue() ** 1.1)
            + (computeFlashlightValue() ** 1.1)
        )
        ** (1.0 / 1.1)) * multiplier

    return totalValue, Accuracy()
