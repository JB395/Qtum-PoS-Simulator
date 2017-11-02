versionNo = "10/20/2017 UTXO Size"     # program version number

'''

Qtum PoS Simulator   Python 3.6.1

Qtum Proof of Stake Simulator

Uses a random number to simulate the behavior of Qtum Proof of Stake mining over long periods
of time.

Uses three nested loops for calculations:

    1. Loop on stake size (outer loop) startingStake size to endingStakeSize, increment
       stakeSizeIncrement

    2. Loop on year - can loop for many years to even out the random probability

    3. Loop on block number within a year - 0 to 246375-1, number of 128 second blocks in
       a year

Block rewards mature in 501 blocks. The array blocksMaturing[] keeps track of when a
block reward will mature 501 blocks in the future.

numSimulRewards (number of simultaneous rewards) keeps track of the number of simultaneous
reward periods. This number could range from 0 (no reward in effect) to 18+ (for whales).
The variable numSimulRewards is used in 3 ways:

    1) Index into the array blocksMaturing[] to track (by block number) when an indivudual
       reward matures
       
    2) To adjust the probablitliy of a new reward while another reward period (or multiple
       simultaneous) rewards are in effect. This is more a factor for whales. The adjustment is

           P(reward) = my weight - (stake size * nunSimulRewards)) / network weight

    3) Track the maximum value reached, just for fun         

    blocksMaturing                          Pop, reached block 1050
    [0]  not used                           [0]  not used
    [1]  1050                               [1]  1263
    [2]  1263                               [2]  1355
    [3]  1355     <- numSimulRewards = 3    [3]  0

numSimulRewards always points to array location with the highest number maturing block reward.
The first maturing block found will be in blocksMaturing[1]. When numSimulRewards == 0 we
are not in a reward period.

'''

import random               # for random
from array import *         # for arrays

startingMyWeight = 1482     # number of coins in wallet
startingStakeSize = 100     # size of coins being staked, starting size
endingStakeSize = 100       # ending size
stakeSizeIncrement = 100    # increase the stake for each outer loop
transactionFee = 0.0009     # transaction fees for a block, go to the staker
networkWeight = 10000000    # total mature coins available for staking
rewardSize = 4              # number of QTUM in each reward
numYears = 20               # number of years to average for each stake size

maxSimulRewards = 0         # maximum number of simultaneous rewards, all stake sizes, all years
maxNumRewardsPerYear = 0    

# array of blocksMaturing
# an array of Long integers
blocksMaturing=array('L', [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,\
                           0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,\
                           0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,\
                           0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,\
                           0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,\
                           0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,\
                           0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,\
                           0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,\
                           0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,\
                           0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,\
                           0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,\
                           0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,\
                           0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,\
                           0,0,0,0,0,0,0,0,0,0])

myWeight = startingMyWeight
stakeSize = startingStakeSize
maxQTUMEarned = 0       # track the best profits, all the stakes and years
totalQTUMEarned = 0
totalEarnedByYear = 0
numStakes = 0
    
print("myWeight = ", myWeight, "networkWeight = ", networkWeight, "numYears = ", numYears, "\n")
print("startingStakeSize = ", startingStakeSize, "endingStakeSize = ", endingStakeSize, "increment = ", stakeSizeIncrement)

random.seed()

# loop on stakeSize = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

bestStakeSizeOverall = 0    # the best stake size for all sizes evaluated

while stakeSize <= endingStakeSize:

    #  loop on years = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

    year = 0
    sumQTUMEarned = 0       # sum over the individual years

    bestStakeSize = 0       # best stake size for this year
    
    while year < numYears:

        # print("year = ", year)

        # loop on block = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

        # reset at the start of each year, this will throw away any rewards in progress
        # at the end of last year, but, oh well

        block = 0                   # current block
        blockSaved = 0              # location of last block reward
        numRewards = 0              # number of rewards found
        numSimulRewards = 0         # number of simultaneus rewards
        myWeight = startingMyWeight # reset for each outer loop

        # print("year starting = ", year, "myWeight = ", myWeight)
          
        while block < 246375:    # 246375 = 675 128 second blocks/day

            # print("block = ", block)

            # if myWeight - (stakeSize * numSimulRewards) <= 0:
            #     print("Everything staked, exiting inner loop at block = ", block)
            #     break
            
            if random.random() <= float(myWeight - (stakeSize * numSimulRewards)) / float(networkWeight):      # staking with block stake removed

                # print("adjusted weight = ", myWeight - (stakeSize * numSimulRewards))
                    
                # if block overlaps occur, just enter them sequentially onto an array and keep track
                # of the tail and them pop them off one at a time as they mature
                # numSimulRewards gives the number of overlapping rewards (to adjust the probability)

                if numSimulRewards > 0:          # got a new reward while at least one other reward was in effect
                    if numSimulRewards > maxSimulRewards:
                        maxSimulRewards = numSimulRewards
                    # print("Number of simultanous rewards, increasing = ", numSimulRewards)
                    
                numSimulRewards += 1
                
                blocksMaturing[numSimulRewards] = block + 500
                # print("Got reward, numSimulRewards = ", numSimulRewards, "blocksMaturing[numSimulRewards] = ", blocksMaturing[numSimulRewards])
                numRewards += 1
                waitBetweenBlocks = block - blockSaved  # wait in number of blocks
                waitInDays = waitBetweenBlocks / 675    # 675 blocks per day
                print(waitInDays)      
                blockSaved = block
                foundBlock = False
            
            if block == blocksMaturing[1] and block != 0:   # found the end of a block waiting period, first time through doesn't count

                # print("Block matured, block = ", block)

                # pop the stack

                i = 0

                while i < numSimulRewards:     
                    blocksMaturing[i] = blocksMaturing[i + 1]
                    
                    # if i < numSimulRewards:
                    #     print("i = ", i, "blocksMaturing[i] = ", blocksMaturing[i])
                        
                    i += 1

                if numSimulRewards >= 1:
                    numSimulRewards -= 1    

                # if numSimulRewards > -2:          # what is the number of overlaps now?
                #     print("Number of simultaneous rewards, decreasing = ", numSimulRewards)

                # this next addition should be really delayed 500 blocks, but, come on,
                # we're talking about a small amount here 500 blocks early, get a life...
                
                myWeight += rewardSize + transactionFee  # add on the reward + any fees
            
            block += 1

            # end of inner loop on block

        # print("year ending = ", year, "myWeight = ", myWeight)    

        year += 1

        sumQTUMEarned += myWeight - startingMyWeight
        # print("sumQTUMEarned ' ", sumQTUMEarned)

        if sumQTUMEarned > maxQTUMEarned:  # found a new max, save it
            maxQTUMEarned = sumQTUMEarned
            # print("Found a new maxQTUMEarned = ", maxQTUMEarned / numYears)      
            bestStakeSize = stakeSize

        totalQTUMEarned += sumQTUMEarned      
        sumQTUMEarned = 0                # reset for each year

        numStakes += 1
        
        stakeSize += stakeSizeIncrement
        
        # end of loop on year    
                
    # print("stakeSize = ", stakeSize, "numRewards per year = ", numRewards / numYears, "maxSimulRewards =", maxSimulRewards)
    # print("stakeSize = ", stakeSize, "average QTUM per year = ", '{:1.2f}'.format(totalQTUMEarned / numYears))
    # print("maxSimulRewards =", maxSimulRewards)
    
    # if numRewards > maxNumRewardsPerYear:
    #    maxNumRewardsPerYear = numRewards

    if bestStakeSize > bestStakeSizeOverall:
        bestStakeSizeOverall = bestStakeSize 
    
    totalEarnedByYear += totalQTUMEarned
    totalQTUMEarned = 0         # reset for stake size

    # end of loop on stakeSize

# QTUMprofit = myWeight - startingMyWeight

print("Average QTUM earned per year, all stakes = ", totalEarnedByYear / numStakes, '{:1.2f}'.format(100 * totalEarnedByYear / startingMyWeight / numStakes), "%")
print("maxQTUMEarned = ", maxQTUMEarned)
print("Best stake size overall = ", bestStakeSizeOverall, "return = ", '{:1.2f}'.format(100 * maxQTUMEarned / startingMyWeight), "%")








