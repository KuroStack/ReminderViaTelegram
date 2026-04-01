<?php

namespace App\Telegram;

use Telegram\Bot\Laravel\Facades\Telegram;

class Guards
{
    public static function isAdmin(int $userId): bool
    {
        $raw = config('telegram-bot.admin_ids', '');
        if (empty($raw)) {
            return false;
        }
        $ids = array_map('intval', array_filter(explode(',', $raw)));
        return in_array($userId, $ids, true);
    }

    public static function requireAdmin(int $userId, string $callbackQueryId): bool
    {
        if (self::isAdmin($userId)) {
            return true;
        }
        Telegram::answerCallbackQuery([
            'callback_query_id' => $callbackQueryId,
            'text'              => 'Admin access required.',
            'show_alert'        => true,
        ]);
        return false;
    }
}
