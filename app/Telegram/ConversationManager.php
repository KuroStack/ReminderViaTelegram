<?php

namespace App\Telegram;

use App\Models\ConversationState;

class ConversationManager
{
    public function getState(int $userId): ?string
    {
        return ConversationState::where('user_id', $userId)->value('state');
    }

    public function setState(int $userId, string $state, array $payload = []): void
    {
        ConversationState::updateOrCreate(
            ['user_id' => $userId],
            ['state' => $state, 'payload' => $payload, 'updated_at' => now()]
        );
    }

    public function getPayload(int $userId): array
    {
        return ConversationState::where('user_id', $userId)->value('payload') ?? [];
    }

    public function mergePayload(int $userId, array $data): void
    {
        $existing = $this->getPayload($userId);
        ConversationState::updateOrCreate(
            ['user_id' => $userId],
            ['payload' => array_merge($existing, $data), 'updated_at' => now()]
        );
    }

    public function clearState(int $userId): void
    {
        ConversationState::where('user_id', $userId)->delete();
    }
}
